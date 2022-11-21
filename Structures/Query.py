from Structures.Table import Table
from Structures.Column import Column
import Applications.Compilation.ast_factory as AST
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


    def extract_subqueries(self):
        # Get subqueries by getting all but the first select expression
        subqueries = list(self.ast.find_all(exp.Select))[1:]
        # Insert a placeholder for the subqueries
        for subquery in subqueries:
            subquery.replace(AST.create_identifier("__subquery_placeholder__"))
        # Transform the subquery ASTs to instances of Query
        return [Query(subq.sql()) for subq in subqueries]

    def insert_subqueries(self, subqueries):
        def transform(node):
            if isinstance(node, exp.Identifier) and node.name == "__subquery_placeholder__":
                return node.replace(subqueries.pop(0).ast)
            return node

        self.ast = self.ast.transform(transform)
        