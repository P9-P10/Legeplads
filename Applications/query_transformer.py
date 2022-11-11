from Structures.Query import Query
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Changes import *
from sqlglot import exp
from Applications.exceptions import *

class RangeTable:
    def __init__(self, from_expressions: list[exp.Expression], join_expressions: list[exp.Expression]):
        self.from_expressions = from_expressions
        self.join_expressions = join_expressions
        self.table = []
        self.create_range_table()
        self.table_names = [name for (name, _alias) in self.table]

    def create_range_table(self):
        # To get the range table
        # Find the tables present in the from expressions
        for expression in self.from_expressions:
            self.table.append(self.create_range_table_entry(expression))
        # Find the tables present in the joins
        if self.join_expressions:
            for expression in self.join_expressions:
                # All elements in the list should be of type exp.JOIN where the attribute 'this' is the relation identifier
                self.table.append(self.create_range_table_entry(expression.this))

    def create_range_table_entry(self, expression):
        if isinstance(expression, exp.Alias):
            return(expression.this.name, expression.alias)
        elif isinstance(expression, exp.Table):
            return(expression.name, "")

    def append(self, item):
        # Add element to list
        self.table.append(item)
        # Add name to list of names
        name, _alias = item
        self.table_names.append(name)
        # Return the index of the added item
        return len(self.table) - 1

    def contains(self, table_name):
        return table_name in self.table_names

    def index_of_entries_with_name(self, table_name):
        return [index for index, (name, _alias) in enumerate(self.table) if name == table_name]


class Selection:
    def __init__(self, db_structure: DatabaseStructure, range_table: RangeTable):
        self.selection_list = []
        self.db = db_structure
        self.range_table = range_table

    def from_star_expression(self):
        for index, (table_name, alias) in enumerate(self.range_table.table):
            columns_in_table = self.db.get_columns_in_table(table_name)
            self.selection_list.extend([(column_name, index) for column_name in columns_in_table])
        return self.selection_list

    def from_expressions(self, expressions: list[exp.Expression]):
        for expression in expressions:
            # Assumption: All expressions are columns
            column_name = expression.name
            # if the column uses an alias
            if expression.table:
                # The alias is either the full name of the table or an alias
                column_alias = expression.table
                for table_name, alias in self.range_table.table:
                    if column_alias == table_name or column_alias == alias:
                        self.selection_list.append((column_name, self.range_table.table.index((table_name, alias))))
            # Otherwise we need the database structure to find what table a column belongs to
            else:
                all_table_names = [entry[0] for entry in self.range_table.table]
                table_name = self.db.table_containing_column(column_name, all_table_names)
                self.selection_list.append((column_name, self.range_table.table.index((table_name, ""))))
        return self.selection_list

    def change_source_relation_for_column(self, column_name: str, current_source_name: str, new_source_index: int):
        indicies = self.range_table.index_of_entries_with_name(current_source_name)
        new_list = []
        for name, index in self.selection_list:
            if name == column_name and index in indicies:
                new_elem = (column_name, new_source_index)
            else:
                new_elem = (name, index)
            new_list.append(new_elem)

        self.selection_list = new_list

class Transformer:
    def __init__(self, old_db_structure: DatabaseStructure, new_db_structure: DatabaseStructure):
        self.old_db = old_db_structure
        self.new_db = new_db_structure


    def transform(self, query: Query, changes):
        self.query = query
        self.ast = query.get_ast()
        self.from_subtree = self.ast.find(exp.From)

        self.verify_selection_is_valid_given_structure(self.old_db)
        self.preprocess_query()

        self.apply_changes(changes)
        
        self.postprocess_query()
        self.verify_selection_is_valid_given_structure(self.new_db)


    def preprocess_query(self):
        self.create_range_table()
        self.create_selection_list()
        
        
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
        self.remove_unused_tables()
        self.ensure_from_not_empty()


    def move_column(self, change):
        # Is this condition even necessary? Do we ever want to use an existing relation?
        if not self.range_table.contains(change.dst_table_name):
                    # Add it to the query
            self.add_table_to_query(change.dst_table_name)
            new_table_index = self.range_table.append((change.dst_table_name, ""))
        else:
                    # Find the first occurence of the table in the range_table
            new_table_index = self.range_table.index_of_entries_with_name(change.dst_table_name)[0]
        self.selection.change_source_relation_for_column(change.column_name, change.src_table_name, new_table_index)
        self.selection_list = self.selection.selection_list

    def adjust_query_select_expression(self):
        if not self.select_star:
            # Adjust the selection expression
            selection_expressions = []
            for column_name, table_index in self.selection_list:
                table_name, alias = self.range_table.table[table_index]
                selection_expressions.append(self.query.create_column(column_name, alias))

            self.query.ast.set('expressions', selection_expressions)

    def remove_unused_tables(self):
        for index, (table, alias) in enumerate(self.range_table.table):
            used = False
            for _name, table_index in self.selection_list:
                if table_index == index:
                    used = True
            if not used:
                self.remove_table_from_query(table)

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


    def add_table_to_query(self, table_name):
        if len(list(self.from_subtree.find_all(exp.Table))) > 0: # If there are other tables in the query
            self.add_join_without_condition(table_name)
        else:
            self.ast.set("from", self.query.create_from_with_table(table_name))


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
            first_join = self.ast.args['joins'].pop(0)
            self.ast.find(exp.From).replace(self.query.create_from_with_table(first_join.this.name))
        

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