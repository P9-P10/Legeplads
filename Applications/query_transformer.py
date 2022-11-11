from Structures.Query import Query
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Changes import *
from sqlglot import exp
from Applications.exceptions import *

class Transformer:
    def __init__(self, old_db_structure: DatabaseStructure, new_db_structure: DatabaseStructure):
        self.old_db = old_db_structure
        self.new_db = new_db_structure


    def transform(self, query: Query, changes):
        self.query = query
        self.ast = ast = query.get_ast()
        self.from_subtree = ast.find(exp.From)

        # Verify selection in input query is valid
        self.verify_selection_is_valid_given_structure(self.old_db)

        # List of (table_name, alias) tuples, where alias is empty string if table has no alias
        self.range_table = self.create_range_table()
        # List of (column_name, relation_index) tuples where relation_index is the index of the source table in the range_table
        self.selection_list = self.create_selection_list(self.range_table)

        for change in changes:
            if isinstance(change, RemoveTable):
                self.remove_table_from_query(change.table_name)
            elif isinstance(change, AddTable):
                self.add_table_to_query(change.table_name)
            elif isinstance(change, MoveColumn):
                # Need to find that column in the selection list
                # and then change it to point to the new column
                self.selection_list = list(map(self.change_matching_selection(change), self.selection_list))
                # Also need to handle changes in join conditions

        if not self.select_star:
            # Adjust the selection expression
            selection_expressions = []
            for column_name, table_index in self.selection_list:
                table_name, alias = self.range_table[table_index]
                selection_expressions.append(self.query.create_column(column_name, alias))

            self.query.ast.set('expressions', selection_expressions)


        # Remove tables that are unused
        for index, (table, alias) in enumerate(self.range_table):
            used = False
            for _name, table_index in self.selection_list:
                if table_index == index:
                    used = True
            if not used:
                self.remove_table_from_query(table)

        self.ensure_from_not_empty()

        # Verify selection in output query is valid
        self.verify_selection_is_valid_given_structure(self.new_db)

    def change_matching_selection(self, change):
        def fun(entry):
            column_name, relation_index = entry
            if change.column_name == column_name:
                # This is the column that we wish to move
                current_table = change.src_table_name
                destination_table = change.dst_table_name
                # First, ensure that the destination table is in the query
                if not destination_table in [name for (name, _alias) in self.range_table]: # TODO: Create class for range_table
                    # Add it to the query
                    self.add_table_to_query(destination_table)
                    self.range_table.append((destination_table, ""))
                    new_table_index = len(self.range_table) - 1
                    pass
                else:
                    # Find the first occurence of the table in the range_table
                    # This is not the best way of doing it
                    new_table_index = self.range_table.index([(name, alias) for (name, alias) in self.range_table if name == destination_table][0])
                # Change the column to point to the new table
                return (column_name, new_table_index)
            else:
                return (column_name, relation_index)
        return fun

    def create_range_table(self):
        range_table = []
        # To get the range table
        # Find the tables present in the from expressions
        for expression in self.query.ast.args['from'].expressions:
            range_table.append(self.create_range_table_entry(expression))
        # Find the tables present in the joins
        if 'joins' in self.query.ast.args.keys():
            for expression in self.query.ast.args['joins']:
                # All elements in the list should be of type exp.JOIN where the attribute 'this' is the relation identifier
                range_table.append(self.create_range_table_entry(expression.this))
        return range_table

    def create_range_table_entry(self, expression):
        if isinstance(expression, exp.Alias):
            return(expression.this.name, expression.alias)
        elif isinstance(expression, exp.Table):
            return(expression.name, "")


    def create_selection_list(self, range_table):
        selection_list = []
        for expression in self.ast.expressions:
            if isinstance(expression, exp.Star):
                self.select_star = True
                for index, (table_name, alias) in enumerate(range_table):
                    columns_in_table = self.old_db.get_columns_in_table(table_name)
                    selection_list.extend([(column_name, index) for column_name in columns_in_table])
                break
            else:
                self.select_star = False
                # Assumption: All expressions are columns
                column_name = expression.name
                # if the column uses an alias
                if expression.table:
                    # The alias is either the full name of the table or an alias
                    column_alias = expression.table
                    for table_name, alias in range_table:
                        if column_alias == table_name or column_alias == alias:
                            selection_list.append((column_name, range_table.index((table_name, alias))))
                # Otherwise we need the database structure to find what table a column belongs to
                else:
                    all_table_names = [entry[0] for entry in range_table]
                    table_name = self.old_db.table_containing_column(column_name, all_table_names)
                    selection_list.append((column_name, range_table.index((table_name, ""))))

        return selection_list


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