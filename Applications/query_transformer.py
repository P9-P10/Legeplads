from Structures.Query import Query
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Changes import *
from sqlglot import exp
from Applications.exceptions import *
from Applications.Parsing import *
from Applications.Compilation.compilers import *


class Transformer:
    def __init__(self, old_db_structure: DatabaseStructure, new_db_structure: DatabaseStructure):
        self.old_db = old_db_structure
        self.new_db = new_db_structure


    def transform(self, query: Query, changes):
        self.query = query
        self.ast = query.get_ast()

        # Only handle SELECT queries
        if len(list(self.ast.find_all(exp.Select))) == 0:
            return

        # Extract and transform subqueries separately
        subqueries = self.query.extract_subqueries()
        for subquery in subqueries:
            Transformer(self.old_db, self.new_db).transform(subquery, changes)

        self.preprocess_query()
        self.apply_changes(changes)
        self.postprocess_query()

        self.query.insert_subqueries(subqueries)


    def preprocess_query(self):
        self.verify_selection_is_valid_given_structure(self.old_db)
        parser = Parser(self.old_db)
        range_table, selection, join_tree = parser.parse(self.ast)
        self.range_table = range_table
        self.selection = selection
        self.join_tree = join_tree
        self.other_expressions = parser.get_other_expressions()

        
    def apply_changes(self, changes):
        for change in changes:
            if isinstance(change, RemoveTable):
                self.remove_table_from_query(change)
            elif isinstance(change, AddTable):
                self.add_table_to_query(change.table_name)
            elif isinstance(change, MoveColumn):
                self.move_column(change)
            elif isinstance(change, ReplaceTable):
                self.replace_table(change)


    def postprocess_query(self):
        self.resolve_ambiguities()
        self.remove_unused_tables()
        self.expr_compiler = ExpressionCompiler(self.range_table)
        self.adjust_query_from_expression()
        self.adjust_query_select_expression()
        self.adjust_query_join_expressions()
        self.adjust_other_expressions()


    def remove_table_from_query(self, change):
        # Find and remove all instances of that table
        for index in self.range_table.index_of_entries_with_name(change.table_name):
            relation = self.range_table.get_relation_with_index(index)
            self.remove_relation_from_query(relation)


    def move_column(self, change):
        if change.src_table_name not in self.range_table.relation_names:
            return
        new_table_index = self.get_existing_or_create_new_relation(change.dst_table_name)
        indicies_to_replace = self.range_table.index_of_entries_with_name(change.src_table_name)
        self.change_all_references_to_relations(indicies_to_replace, new_table_index)
        

    def change_all_references_to_relations(self, indicies_to_replace: list[int], new_index: int):
        self.selection.change_references_to_relations_in_attributes(indicies_to_replace, new_index)
        self.join_tree.change_references_to_relations_in_attributes(indicies_to_replace, new_index)
        self.join_tree.where_expr.change_references_to_relations_in_attributes(indicies_to_replace, new_index)

        for expression in self.other_expressions:
            expression.change_references_to_relations_in_attributes(indicies_to_replace, new_index)


    def replace_table(self, change):
        if change.old_table_name not in self.range_table.relation_names:
            return

        indicies_to_replace = self.range_table.index_of_entries_with_name(change.old_table_name)
        
        for old_index in indicies_to_replace:
            new_index = self.add_table_to_query(change.new_table_name)
            self.move_alias_to_new_relation(old_index, new_index)
            self.change_all_references_to_relations([old_index], new_index)
            self.join_tree.move_condition([old_index], new_index)
            self.remove_relation_from_query(self.range_table.get_relation_with_index(old_index))


    def move_alias_to_new_relation(self, old_index, new_index):
        new_relation = self.range_table.get_relation_with_index(new_index)
        old_relation = self.range_table.get_relation_with_index(old_index)
        new_relation.change_alias(old_relation.alias)


    def get_existing_or_create_new_relation(self, relation_name: str):
        if not self.range_table.contains(relation_name):
            # Add it to the query
            return self.add_table_to_query(relation_name)
        else:
            # Find the first occurence of the table in the range_table
            return self.range_table.index_of_entries_with_name(relation_name)[0]


    # Compilation
    def adjust_query_select_expression(self):
        selection_expressions = SelectionCompiler(self.expr_compiler).compile(self.selection)
        self.query.ast.set('expressions', selection_expressions)


    # Compilation
    def adjust_query_from_expression(self):      
        from_expr, where_expr = FromExprCompiler(self.range_table, self.expr_compiler).compile(self.join_tree) 
        self.ast.set('from', from_expr)
        if where_expr:
            self.ast.args['where'] = where_expr


    # Compilation
    def adjust_query_join_expressions(self):
        new_joins = JoinTreeCompiler(self.expr_compiler).compile(self.join_tree)
        self.query.ast.set('joins', new_joins)


    # Compliation
    def adjust_other_expressions(self):
        new_expressions = GroupbyAndOrderbyCompiler(self.expr_compiler).compile(self.other_expressions)
        for old_expr, new_expr in zip(self.other_expressions, new_expressions):
            old_expr.ast.replace(new_expr)


    def remove_unused_tables(self):
        for unused_relation in self.selection.get_unused_relations():
            if unused_relation.index not in self.join_tree.relations_used_in_conditions():
                self.remove_relation_from_query(unused_relation)


    def add_table_to_query(self, table_name):
        new_table_index = self.range_table.append(table_name, "")
        self.join_tree.add_relation_without_condition(new_table_index)
        return new_table_index


    def remove_relation_from_query(self, relation):
        self.join_tree.remove_relation(relation)
        self.join_tree.from_indicies = [index for index in self.join_tree.from_indicies if not index == relation.index]
        
    
    def resolve_ambiguities(self):
        for expr in self.selection.selection_list:
            for attribute in expr.attributes:
                if len(self.new_db.get_tables_containing_column(attribute.name)) > 1:
                    relation = self.range_table.get_relation_with_index(attribute.relation_index)
                    if relation.alias == "" or relation.alias == relation.name:
                        relation.change_alias(relation.name)


    # parsing
    def verify_selection_is_valid_given_structure(self, structure: DatabaseStructure):
        column_nodes_in_expressions = self.flatten([list(expression.find_all(exp.Column)) for expression in self.ast.expressions])
        column_names_in_selection = [column.name for column in column_nodes_in_expressions]

        table_nodes_in_from_expression = list(self.ast.find(exp.From).find_all(exp.Table))
        table_names = [table.name for table in table_nodes_in_from_expression]
        # This part is sort of sketchy
        # Need to somehow encapsulate selection and joins
        table_nodes_in_joins = self.flatten([list(join.find_all(exp.Table)) for join in self.query.get_join_expressions()])
        table_names.extend([table.name for table in table_nodes_in_joins])
        
        for column_name in column_names_in_selection:
            if not structure.is_column_in_tables(column_name, table_names):
                raise InvalidSelectionException(f'Column {column_name} is not present in the tables {",".join(table_names)}')


    def flatten(self, list):
        return [item for sublist in list for item in sublist]
