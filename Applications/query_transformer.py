from Structures.Query import Query
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Changes import *
from sqlglot import exp
from Applications.exceptions import *
from Applications.Parsing import *
import Applications.Compilation.ast_factory as AST

class ExpressionCompiler:
    def __init__(self, range_table: RangeTable):
        self.range_table = range_table


    def compile(self, expression: Expression):
        if expression.ast is None:
            return None
        if isinstance(expression.ast, exp.Column):
            self.compile_single_column(expression)
        else:
            self.compile_multiple_columns(expression)
        
        return expression.ast


    def compile_single_column(self, expression: Expression):
        relation = self.range_table.get_relation_for_attribute(expression.attributes[0])
        expression.ast = AST.create_column(expression.attributes[0].name, relation.alias)

    
    def compile_multiple_columns(self, expression: Expression):
        new_columns = [self.compile_attribute(attribute) for attribute in expression.attributes]
        # Each column should correspond to an attribute
        for column, new_column in zip(expression.ast.find_all(exp.Column), new_columns):
            column.replace(new_column)

        
    def compile_attribute(self, attribute: Attribute) -> exp.Column:
        attr_relation = self.range_table.get_relation_for_attribute(attribute)
        if attr_relation.alias == '':
            relation_name = attr_relation.name
        else:
            relation_name = attr_relation.alias
        return AST.create_column(attribute.name, relation_name)


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
        if not change.old_table_name in self.range_table.relation_names:
            return

        indicies_to_replace = self.range_table.index_of_entries_with_name(change.old_table_name)
        
        for old_index in indicies_to_replace:
            new_index = self.get_index_of_new_relation(change.new_table_name)
            self.move_alias_to_new_relation(old_index, new_index)
            self.change_all_references_to_relations([old_index], new_index)
            self.join_tree.move_condition([old_index], new_index)
            self.remove_relation_from_query(self.range_table.get_relation_with_index(old_index))


    def move_alias_to_new_relation(self, old_index, new_index):
        new_relation = self.range_table.get_relation_with_index(new_index)
        old_relation = self.range_table.get_relation_with_index(old_index)
        new_relation.change_alias(old_relation.alias)


    def get_index_of_new_relation(self, relation_name: str):
        return self.add_table_to_query(relation_name)


    def get_existing_or_create_new_relation(self, relation_name: str):
        if not self.range_table.contains(relation_name):
            # Add it to the query
            return self.add_table_to_query(relation_name)
        else:
            # Find the first occurence of the table in the range_table
            return self.range_table.index_of_entries_with_name(relation_name)[0]


    def adjust_query_select_expression(self):
        compiler = ExpressionCompiler(self.range_table)
        selection_expressions = []
        for expr in self.selection.selection_list:
            selection_expressions.append(compiler.compile(expr))

        self.query.ast.set('expressions', selection_expressions)


    def adjust_query_join_expressions(self):
        new_joins = []
        compiler = ExpressionCompiler(self.range_table)
        for join in self.join_tree.joins:
            # Change the columns in the condition
            if join.expression.ast:
                compiler.compile(join.expression)
                
            relation = self.range_table.get_relation_with_index(join.relation_index)
            alias = None if relation.alias == "" else relation.alias
            new_joins.append(AST.create_join_with_condition(relation.name, join.expression.ast, alias))

        self.query.ast.set('joins', new_joins)


    def adjust_other_expressions(self):
        compiler = ExpressionCompiler(self.range_table)
        new_expressions = []
        for expr in self.other_expressions:
            new_expressions.append(compiler.compile(expr))

        for old_expr, new_expr in zip(self.other_expressions, new_expressions):
            old_expr.ast.replace(new_expr)


    def remove_unused_tables(self):
        for unused_relation in self.selection.get_unused_relations():
            if unused_relation.index not in self.join_tree.relations_used_in_conditions():
                self.remove_relation_from_query(unused_relation)


    def get_relation_from_node(self, node: exp.Expression) -> Relation:
        if isinstance(node, exp.Alias):
            return self.range_table.get_matching_relation(node.this.name, node.alias)
        elif isinstance(node, exp.Table):
            return self.range_table.get_matching_relation(node.name, "")


    def add_table_to_query(self, table_name):
        new_table_index = self.range_table.append(table_name, "")
        self.ensure_table_is_not_ambiguous(table_name)
        # This could be simplified, as the case of an empty 'from' clause is handled.
        # However, that would not communicate the purpose of this operation as effectively
        if len(self.join_tree.from_indicies) > 0: # If there is at least one table in the query
            self.join_tree.add_join_without_condition(new_table_index)
        else:
            self.join_tree.from_indicies = [new_table_index]
            #self.ast.set("from", self.query.create_from_with_table(table_name))
        return new_table_index


    def ensure_table_is_not_ambiguous(self, table_name):
        indicies_of_relations_with_name = self.range_table.index_of_entries_with_name(table_name)
        if len(indicies_of_relations_with_name) > 1:
            for occurence, index in enumerate(indicies_of_relations_with_name):
                relation = self.range_table.get_relation_with_index(index)
                if relation.alias == "" or relation.alias == relation.name:
                    relation.change_alias(relation.name + str(occurence + 1))
                

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


    # Mix of parsing, manipulation, and compilation
    def adjust_query_from_expression(self):               
        # Create and insert from expressions
        expressions = []
        for index in self.join_tree.from_indicies:
            relation = self.range_table.get_relation_with_index(index)
            if relation.alias:
                expressions.append(AST.create_table_with_alias(relation.name, relation.alias))
            else:
                expressions.append(AST.create_table(relation.name))
        self.ast.set('from', exp.From(expressions=expressions))

        # Adjust attributes used in WHERE condition
        if self.join_tree.where_expr.ast:
            compiler = ExpressionCompiler(self.range_table)
            result = compiler.compile(self.join_tree.where_expr)
            self.ast.args['where'] = AST.create_where_with_condition(result)


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