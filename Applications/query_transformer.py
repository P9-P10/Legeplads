from Structures.Query import Query
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Changes import *
from sqlglot import exp
from Applications.exceptions import *

class Relation:
    def __init__(self, name: str, alias: str, index: int):
        self.name = name
        self.alias = alias
        self.index = index
    
    def __repr__(self):
        return f'Relation(Name: {self.name}, Alias: {self.alias}, Index: {self.index})'

class Attribute:
    def __init__(self, name, relation_index):
        self.name = name
        self.relation_index = relation_index

    def __repr__(self):
        return f'Attribute(Name: {self.name}, Relation_index: {self.relation_index})'

class RangeTable:
    def __init__(self, from_expressions: list[exp.Expression], join_expressions: list[exp.Expression]):
        self.from_expressions = from_expressions
        # All elements in the list should be of type exp.JOIN where the attribute 'this' is the relation identifier
        self.join_expressions = join_expressions
        self.relations = []
        self.relation_names = []
        self.populate_range_table()


    def populate_range_table(self):
        all_expressions = self.from_expressions + [join_exp.this for join_exp in self.join_expressions]
        [self.create_range_table_entry(expression) for expression in all_expressions]


    def create_range_table_entry(self, expression):
        if isinstance(expression, exp.Alias):
            self.append(expression.this.name, expression.alias)
        elif isinstance(expression, exp.Table):
            self.append(expression.name, "")


    def append(self, name: str, alias: str) -> int:
        relation = Relation(name, alias, len(self.relations))
        self.relations.append(relation)
        self.relation_names.append(name)
        # Return the index of the added item
        return relation.index


    def contains(self, table_name) -> bool:
        return table_name in self.relation_names

    def index_of_entries_with_name(self, table_name) -> list[int]:
        return [relation.index for relation in self.relations if relation.name == table_name]

    def index_of_matching_relation(self, name: str, alias: str):
        return self.get_matching_relation(name, alias).index
    
    def get_matching_relation(self, name: str, alias: str) -> Relation:
        for relation in self.relations:
            if relation.name == name and relation.alias == alias:
                return relation
                # TODO raise exception if there is no match

    def get_relation_for_attribute(self, attribute: Attribute) -> Relation:
        return self.relations[attribute.relation_index]

    def get_relation_with_alias(self, alias: str):
        for relation in self.relations:
            if relation.alias == alias:
                return relation

        # The alias of a column, can also be the table name
        for relation in self.relations:
            if relation.name == alias:
                return relation
            
        # TODO raise exception if there is no match

class Selection:
    def __init__(self, db_structure: DatabaseStructure, range_table: RangeTable):
        self.selection_list = []
        self.db = db_structure
        self.range_table = range_table

    def from_star_expression(self) -> list[Attribute]:
        for relation in self.range_table.relations:
            columns_in_table = self.db.get_columns_in_table(relation.name)
            self.selection_list.extend([Attribute(column_name, relation.index) for column_name in columns_in_table])
        return self.selection_list

    def from_expressions(self, expressions: list[exp.Expression]) -> list[Attribute]:
        for expression in expressions:
            # Assumption: All expressions are columns
            column_name = expression.name
            # if the column uses an alias
            if expression.table:
                # The alias is either the full name of the table or an alias
                column_alias = expression.table
                for relation in self.range_table.relations:
                    if column_alias == relation.name or column_alias == relation.alias:
                        self.selection_list.append(Attribute(column_name, self.range_table.index_of_matching_relation(relation.name, relation.alias)))
            # Otherwise we need the database structure to find what table a column belongs to
            else:
                table_name = self.db.table_containing_column(column_name, self.range_table.relation_names)
                self.selection_list.append(Attribute(column_name, self.range_table.index_of_matching_relation(table_name, "")))
        return self.selection_list

    def change_source_relation_for_column(self, column_name: str, current_source_name: str, new_source_index: int):
        indicies = self.range_table.index_of_entries_with_name(current_source_name)
        new_list = []
        for attribute in self.selection_list:
            if attribute.name == column_name and attribute.relation_index in indicies:
                new_attr = Attribute(column_name, new_source_index)
            else:
                new_attr = attribute
            new_list.append(new_attr)

        self.selection_list = new_list

class JoinTree:
    def __init__(self, join_expressions: list[exp.Expression], range_table: RangeTable):
        self.range_table = range_table
        # Create a list/tree of joins in the query and their qualifications/conditions
        # The joins should reference relations in the range_table, and the conditions should contain attributes
        self.joins = []
        for node in join_expressions:
            relation = self.get_relation_from_node(node.this)
            attributes = self.get_attributes_from_join_condition(node, relation)
            condition = None
            # Add the 'on' expression node to the tuple if it exists 
            if 'on' in node.args.keys():
                condition = node.args['on'].copy()
            self.joins.append((relation, attributes, condition))


    def get_relation_from_node(self, node: exp.Expression) -> Relation:
        if isinstance(node, exp.Alias):
            return self.range_table.get_matching_relation(node.this.name, node.alias)
        elif isinstance(node, exp.Table):
            return self.range_table.get_matching_relation(node.name, "")


    def get_attributes_from_join_condition(self, node: exp.Expression, relation: Relation) -> list[Attribute]:
        result = []
        for column in node.find_all(exp.Column):
            if column.table:
                result.append(Attribute(column.name, self.range_table.get_relation_with_alias(column.table).index))
            # Otherwise we need the database structure to find what table a column belongs to
            else:
                table_name = self.db.table_containing_column(column.name, self.range_table.relation_names)
                result.append(Attribute(column.name, self.range_table.index_of_matching_relation(table_name, "")))
        return result


    # This is copied from selection, and should be generalised
    def change_source_relation_for_join_conditions(self, column_name: str, current_relation_name: str, new_relation_index: int):
        indicies = self.range_table.index_of_entries_with_name(current_relation_name)
        new_joins = []
        for relation, attributes, expression in self.joins:
            new_list = []
            for attr in attributes:
                if attr.name == column_name and attr.relation_index in indicies:
                    new_attr = Attribute(column_name, new_relation_index)
                else:
                    new_attr = attr
                new_list.append(new_attr)
            new_joins.append((relation, new_list, expression))

        self.joins = new_joins

    def add_join_without_condition(self, table_name):
        relation = self.range_table.get_matching_relation(table_name, "")
        self.joins.append((relation, [], None))


class Transformer:
    def __init__(self, old_db_structure: DatabaseStructure, new_db_structure: DatabaseStructure):
        self.old_db = old_db_structure
        self.new_db = new_db_structure


    def transform(self, query: Query, changes):
        self.query = query
        self.ast = query.get_ast()
        self.from_subtree = self.ast.find(exp.From)

        self.preprocess_query()
        self.apply_changes(changes)
        self.postprocess_query()


    def preprocess_query(self):
        self.verify_selection_is_valid_given_structure(self.old_db)
        self.create_range_table()
        self.create_selection_list()
        self.create_join_tree()
        
        
    def apply_changes(self, changes):
        for change in changes:
            if isinstance(change, RemoveTable):
                self.remove_table_from_query(change.table_name)
            elif isinstance(change, AddTable):
                self.add_table_to_query(change.table_name)
            elif isinstance(change, MoveColumn):
                self.move_column(change)



    def postprocess_query(self):
        self.adjust_query_select_expression()
        self.adjust_query_join_expressions()
        self.remove_unused_tables()
        self.ensure_from_not_empty()
        self.verify_selection_is_valid_given_structure(self.new_db)


    def move_column(self, change):
        # Is this condition even necessary? Do we ever want to use an existing relation?
        if not self.range_table.contains(change.dst_table_name):
            # Add it to the query
            new_table_index = self.add_table_to_query(change.dst_table_name)
        else:
            # Find the first occurence of the table in the range_table
            new_table_index = self.range_table.index_of_entries_with_name(change.dst_table_name)[0]
        self.selection.change_source_relation_for_column(change.column_name, change.src_table_name, new_table_index)
        if self.join_tree:
            self.join_tree.change_source_relation_for_join_conditions(change.column_name, change.src_table_name, new_table_index)
        self.selection_list = self.selection.selection_list

    # TODO move to an expression class
    def adjust_query_select_expression(self):
        if not self.select_star:
            # Adjust the selection expression
            selection_expressions = []
            for attribute in self.selection_list:
                relation = self.range_table.get_relation_for_attribute(attribute)
                selection_expressions.append(self.query.create_column(attribute.name, relation.alias))

            self.query.ast.set('expressions', selection_expressions)

    # TODO move to a join class
    # TODO or move to an expression class
    def adjust_query_join_expressions(self):
        if not self.join_tree:
            return
        new_joins = []
        for relation, attributes, condition in self.join_tree.joins:
            # Change the columns in the condition
            if condition:
                for column, attr in zip(condition.find_all(exp.Column), attributes):
                    attr_relation = self.range_table.get_relation_for_attribute(attr)
                    if attr_relation.alias == '':
                        relation_name = attr_relation.name
                    else:
                        relation_name = attr_relation.alias
                    column.replace(self.query.create_column(attr.name, relation_name))
                
            new_joins.append(self.query.create_join_with_condition(relation.name, condition))
        self.query.ast.set('joins', new_joins)


    def remove_unused_tables(self):
        if not self.select_star:
            for relation in self.range_table.relations:
                used = False
                for attribute in self.selection_list:
                    if attribute.relation_index == relation.index:
                        used = True
                if not used:
                    self.remove_table_from_query(relation.name)

    def create_range_table(self):
        # List of (table_name, alias) tuples, where alias is empty string if table has no alias
        if 'joins' in self.query.ast.args.keys():
             joins = self.query.ast.args['joins']
        else:
            joins = []
        self.range_table = RangeTable(self.query.ast.args['from'].expressions, joins)

    def create_selection_list(self):
        # List of (column_name, relation_index) tuples where relation_index is the index of the source table in the range_table
        self.selection = Selection(self.old_db, self.range_table)

        if isinstance(self.ast.expressions[0], exp.Star):
            self.select_star = True
            self.selection_list = self.selection.from_star_expression()
        else:
            self.select_star = False
            self.selection_list = self.selection.from_expressions(self.ast.expressions)

    def create_join_tree(self):
        if 'joins' in self.query.ast.args.keys():
            self.join_tree = JoinTree(self.query.ast.args['joins'], self.range_table)
        else:
            self.join_tree = JoinTree([], self.range_table)


    def get_relation_from_node(self, node: exp.Expression) -> Relation:
        if isinstance(node, exp.Alias):
            return self.range_table.get_matching_relation(node.this.name, node.alias)
        elif isinstance(node, exp.Table):
            return self.range_table.get_matching_relation(node.name, "")


    def get_attributes_from_join_condition(self, node: exp.Expression, relation: Relation) -> list[Attribute]:
        result = []
        for column in node.find_all(exp.Column):
            if column.table:
                result.append(Attribute(column.name, self.range_table.get_relation_with_alias(column.table).index))
            # Otherwise we need the database structure to find what table a column belongs to
            else:
                table_name = self.db.table_containing_column(column.name, self.range_table.relation_names)
                result.append(Attribute(column.name, self.range_table.index_of_matching_relation(table_name, "")))
        return result


    def change_source_relation_for_join_conditions(self, column_name: str, current_relation_name: str, new_relation_index: int):
        indicies = self.range_table.index_of_entries_with_name(current_relation_name)
        new_joins = []
        for relation, attributes in self.joins:
            new_list = []
            for attr in attributes:
                if attr.name == column_name and attr.relation_index in indicies:
                    new_attr = Attribute(column_name, new_relation_index)
                else:
                    new_attr = attr
                new_list.append(new_attr)
            new_joins.append((relation, new_list))

        self.joins = new_joins

    def add_table_to_query(self, table_name):
        new_table_index = self.range_table.append(table_name, "")
        if len(list(self.from_subtree.find_all(exp.Table))) > 0: # If there are other tables in the query
            self.join_tree.add_join_without_condition(table_name)
        else:
            self.ast.set("from", self.query.create_from_with_table(table_name))
        return new_table_index


    def add_join_without_condition(self, table_name):
        self.ast.append("joins", self.query.create_simple_join(table_name))


    def remove_table_from_query(self, table_name):
        # Remove from 'From' expression
        self.remove_table_from_tree(self.from_subtree, table_name)
        # Remove from joins
        # This may need to be more general in order to handle aliases
        for node in self.ast.find_all(exp.Join):
            if node.this.name == table_name:
                node.pop()
        self.remove_nodes_from_tree(self.ast, exp.Join, lambda node: node.this.name == table_name)


    def ensure_from_not_empty(self):
        # Check if 'From' expression is now empty
        # If so one of the tables from join needs to be inserted
        selection = list(self.ast.find(exp.From).expressions)
        if len(selection) == 0:
            # find and remove the first join, 
            # take the element from the join and insert it into from
            # If it has a join condition, put that into the where clause
            first_join = self.ast.args['joins'].pop(0)
            self.ast.find(exp.From).replace(self.query.create_from_with_table(first_join.this.name))
            # If the moved join had a condition, move it to the where clause
            if 'on' in first_join.args.keys() and first_join.args['on']:
                self.ast.args['where'] = self.query.create_where_with_condition(first_join.args['on'])

        

    def remove_table_from_tree(self, tree, table_name):
        self.remove_nodes_from_tree(tree, exp.Alias, lambda alias_node: alias_node.this.name == table_name)
        self.remove_nodes_from_tree(tree, exp.Table, lambda table_node: table_node.name == table_name)


    def remove_nodes_from_tree(self, tree, node_type, condition_fun):
        for node in tree.find_all(node_type):
            if condition_fun(node):
                node.pop()

    
    def add_alias_to_table(self, table_name: str, alias: str):
        # TODO Create find_table function
        for node in self.ast.find_all(exp.Table):
            if node.name == table_name:
                node.replace(self.query.create_table_with_alias(table_name, alias))


    def verify_selection_is_valid_given_structure(self, structure: DatabaseStructure):
        column_nodes_in_expressions = self.flatten([list(expression.find_all(exp.Column)) for expression in self.ast.expressions])
        column_names_in_selection = [column.name for column in column_nodes_in_expressions]

        table_nodes_in_from_expression = list(self.ast.find(exp.From).find_all(exp.Table))
        table_names = [table.name for table in table_nodes_in_from_expression]
        # This part is sort of sketchy
        # Need to somehow encapsulate selection and joins
        if 'joins' in self.ast.args.keys():
            table_nodes_in_joins = self.flatten([list(join.find_all(exp.Table)) for join in self.ast.args['joins']])
            table_names.extend([table.name for table in table_nodes_in_joins])
        
        
        for column_name in column_names_in_selection:
            if not structure.is_column_in_tables(column_name, table_names):
                raise InvalidSelectionException(f'Column {column_name} is not present in the tables {",".join(table_names)}')


    def flatten(self, list):
        return [item for sublist in list for item in sublist]