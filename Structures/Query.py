from Structures.Table import Table
from Structures.Column import Column
import sqlglot
from sqlglot import parse_one, exp

class Query:
    def __init__(self, query_as_string: str):
        self.query_as_string = query_as_string
        try:
            self.ast = parse_one(query_as_string)
        except sqlglot.ParseError:
            raise ValueError("The query is not valid SQL")

    def __str__(self):
        return self.ast.sql()

    def __eq__(self, other):
        if isinstance(other, Query):
            if str(other) == str(self):
                return True
        return False

    def __repr__(self):
        return str(self)

    def get_ast(self) -> exp.Expression:
        return self.ast

    # def transform_ast(self, transformer):
    #     self.ast = self.ast.transform(transformer)

    # def replace_table(self, old_table: Table, new_table: Table):
    #     self.replace_matching_identifers(old_table.name, new_table.name)

    # def replace_matching_identifers(self, old_name, new_name):
    #     def transform(node):
    #         if isinstance(node, exp.Identifier) and node.name == old_name:
    #             return node.replace(self.create_identifier(new_name))
    #         return node

    #     self.transform_ast(transform)


    # def replace_column(self, old_column: Column, new_column: Column):
    #     def transform(node):
    #         if isinstance(node, exp.Column) and node.name == str(old_column):
    #             alias = self.get_alias_for_column(node, new_column)
    #             return node.replace(self.create_column(new_column.name, alias))
    #         return node

    #     self.transform_ast(transform)

    # def get_alias_for_column(self, node: exp.Column, new_column: Column) -> str:
    #     # Only replace alias if one is defined on the new column
    #     if new_column.get_alias():
    #         alias = new_column.get_alias()
    #     else:
    #         alias = node.table
    #     return alias

    def create_column(self, name, table=None):
        if table:
            return exp.Column(
                this=self.create_identifier(name),
                table=self.create_identifier(table)
            )
        else:
            return exp.Column(this=self.create_identifier(name))

    def create_identifier(self, name: str):
        return exp.Identifier(this=name)

    def create_table(self, name: str):
        return exp.Table(this=self.create_identifier(name))

    def create_simple_join(self, table_name: str):
        return exp.Join(this=self.create_table(table_name))

    def create_from_with_table(self, table_name: str):
        return exp.From(expressions=[self.create_table(table_name)])

    # def get_tables(self):
    #     # Returns all tables in the query, if they have an alias, this is also included
    #     # The tables do not have their columns
    #     all_tables = self.get_all_tables()
    #     tables_with_aliases = self.get_tables_with_aliases()
    #     tables_without_aliases = [table for table in all_tables if table not in tables_with_aliases]

    #     return tables_without_aliases + tables_with_aliases

    # def get_tables_with_aliases(self):
    #     table_alias_nodes = self.get_aliases()
    #     return [self.create_table_from_alias_node(node) for node in table_alias_nodes]

    # def create_table_from_alias_node(self, alias_node: exp.Alias) -> Table:
    #     table = Table(alias_node.this.name)
    #     table.set_alias(alias_node.alias)
    #     return table

    # def get_all_tables(self):
    #     table_nodes = self.get_all_instances(exp.Table)
    #     return [Table(node.name) for node in table_nodes]


    # def get_aliases(self):
    #     return self.get_alias_nodes()

    # def get_all_instances(self, type):
    #     return self.ast.find_all(type)

    # def get_columns(self):
    #     column_nodes = self.get_all_instances(exp.Column)
    #     return self.remove_duplicates([self.create_column_from_node(node) for node in column_nodes])

    # def create_column_from_node(self, node: exp.Column) -> Column:
    #     if node.table:
    #         return Column(node.name, node.table)
    #     else:
    #         return Column(node.name)

    # def remove_duplicates(self, input_list):
    #     return set(input_list)

    # def has_star_expression(self) -> bool:
    #     if self.ast.find(exp.Star):
    #         return True
    #     else:
    #         return False

    # def add_to_select(self, columns: list[Column]):

    #     def create_columns_from_list():
    #         return [self.create_column(column.name, column.alias) for column in columns]

    #     def transform(node):
    #         if isinstance(node, exp.Select) and not node.find(exp.Star):
    #             node.expressions.extend(create_columns_from_list())
    #             return node
    #         elif isinstance(node, exp.Star):
    #             return create_columns_from_list()
    #         return node

    #     self.transform_ast(transform)

    # def get_alias_nodes(self):
    #     return self.get_all_instances(exp.Alias)

    # def get_table_nodes(self):
    #     return self.get_all_instances(exp.Table)

    # def get_column_nodes(self):
    #     return self.get_all_instances(exp.Column)

    # def extract_subqueries(self):
    #     # Get subqueries by getting all but the first select expression
    #     subqueries = list(self.get_all_instances(exp.Select))[1:]
    #     # Insert a placeholder for the subqueries
    #     for subquery in subqueries:
    #         subquery.replace(self.create_identifier("__subquery_placeholder__"))
    #     # Transform the subquery ASTs to instances of Query
    #     return [Query(subq.sql()) for subq in subqueries]

    # def insert_subqueries(self, subqueries):
    #     def transform(node):
    #         if isinstance(node, exp.Identifier) and node.name == "__subquery_placeholder__":
    #             return node.replace(subqueries.pop(0).ast)
    #         return node

    #     self.transform_ast(transform)
        