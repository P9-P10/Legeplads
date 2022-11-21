import pytest

from Structures.Query import Query
import Applications.Compilation.ast_factory as AST
from sqlglot import exp

def test_query_get_from_expressions():
    query = Query("Select * from test_table")
    expected = [exp.Table(this=exp.Identifier(this="test_table"))]

    assert query.get_from_expressions() == expected

def test_query_get_join_expressions_with_no_joins():
    query = Query("Select * from test_table")
    expected = []

    assert query.get_join_expressions() == expected

def test_query_get_join_expressions_with_joins():
    query = Query("Select * from test_table join first_other_table join second_other_table")
    expected = [AST.create_simple_join("first_other_table"), AST.create_simple_join("second_other_table")]

    assert query.get_join_expressions() == expected

def test_query_get_where_expression_without_where():
    query = Query("Select * from test_table")
    expected = []

    assert query.get_where_expression() == expected

def test_query_get_where_expression_with_where():
    query = Query("Select * from test_table where a = b")
    expected = exp.EQ(this=AST.create_column("a"), expression=AST.create_column("b"))

    assert query.get_where_expression() == expected
