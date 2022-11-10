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
        self.selection = list(ast.expressions)

        for change in changes:
            if isinstance(change, RemoveTable):
                self.remove_table_from_query(change.table_name)
            elif isinstance(change, AddTable):
                self.add_table_to_query(change.table_name)
            elif isinstance(change, MoveColumn):
                if len(self.selection) == 1 and self.selection[0].name == change.column_name:
                    self.remove_table_from_query(change.src_table_name)
                    self.add_table_to_query(change.dst_table_name)
                else:
                    self.add_table_to_query(change.dst_table_name)

        self.ensure_from_not_empty()

        # Verify selection in output query is valid
        self.verify_selection_is_valid_given_structure(self.new_db)


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
        self.remove_nodes_from_tree(tree, exp.Table, lambda table_node: table_node.name == table_name)

    def remove_nodes_from_tree(self, tree, node_type, condition_fun):
        for node in tree.find_all(node_type):
            if condition_fun(node):
                node.pop()

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
            if not structure.column_in_tables(column_name, table_names):
                raise InvalidSelectionException(f'Column {column_name} is not present in the tables {",".join(table_names)}')


    def flatten(self, list):
        return [item for sublist in list for item in sublist]