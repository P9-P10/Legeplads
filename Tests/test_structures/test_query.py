import pytest

from Structures.Query import Query
from Structures.Table import Table
from Structures.Column import Column
from sqlglot import exp

@pytest.fixture
def empty_query():
    return Query("")

def test_query_create_identifier(empty_query):
    assert empty_query.create_identifier("test") == exp.Identifier(this="test")

def test_query_create_table(empty_query):
    assert empty_query.create_table("test_table") == exp.Table(this=exp.Identifier(this="test_table"))

def test_query_create_simple_join(empty_query):
    assert empty_query.create_simple_join("test_table") == exp.Join(this=exp.Table(this=exp.Identifier(this="test_table")))

def test_query_create_from_expression(empty_query):
    assert empty_query.create_from_with_table("test_table") == exp.From(expressions=[exp.Table(this=exp.Identifier(this="test_table"))])