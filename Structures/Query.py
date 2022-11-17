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

    def get_from_expressions(self):
        return self.ast.args['from'].expressions

    def get_join_expressions(self):
        if 'joins' in self.ast.args.keys():
            return self.ast.args['joins']
        else:
            return []

    def get_where_expression(self):
        if 'where' in self.ast.args.keys():
            return self.ast.args['where'].this
        else:
            return []

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

    def create_simple_join(self, table_name: str, table_alias: str = None):
        if table_alias:
            return exp.Join(this=self.create_table_with_alias(table_name, table_alias))
        else:
            return exp.Join(this=self.create_table(table_name))

    def create_join_with_condition(self, table_name: str, condition: exp.Expression, table_alias: str = None):
        if table_alias:
            return exp.Join(this=self.create_table_with_alias(table_name, table_alias), on=condition)
        else:
            return exp.Join(this=self.create_table(table_name), on=condition)

    def create_from_with_table(self, table_name: str, table_alias: str = None):
        if table_alias:
            return exp.From(expressions=[self.create_table_with_alias(table_name, table_alias)])
        else:
            return exp.From(expressions=[self.create_table(table_name)])

    def create_table_with_alias(self, table_name: str, table_alias: str):
        return exp.Alias(this=self.create_table(table_name), alias=exp.TableAlias(this=self.create_identifier(table_alias)))

    def create_where_with_condition(self, condition: exp.Expression):
        return exp.Where(this=condition)

    def create_star_selection(self):
        return [exp.Star()]


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
        