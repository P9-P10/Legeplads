import pytest

from sqlglot import exp
from Applications.Compilation import *

def test_query_create_identifier():
    assert create_identifier("test") == exp.Identifier(this="test")

def test_query_create_table():
    assert create_table("test_table") == exp.Table(this=exp.Identifier(this="test_table"))

def test_query_create_simple_join():
    assert create_simple_join("test_table") == exp.Join(this=exp.Table(this=exp.Identifier(this="test_table")))

def test_query_create_simple_join_with_alias():
    assert create_simple_join("test_table", "test_alias") == exp.Join(this=create_table_with_alias("test_table", "test_alias"))

def test_query_create_join_with_condition():
    assert create_join_with_condition("test_table", exp.EQ(this=exp.Identifier(this="condition"))) == exp.Join(this=exp.Table(this=exp.Identifier(this="test_table")), on=exp.EQ(this=exp.Identifier(this="condition")))

def test_query_create_join_with_condition_with_alias():
    assert create_join_with_condition("test_table", exp.EQ(this=exp.Identifier(this="condition")), "test_alias") == exp.Join(this=create_table_with_alias("test_table", "test_alias"), on=exp.EQ(this=exp.Identifier(this="condition")))

# TODO: Add case where table has an alias
def test_query_create_from_expression():
    assert create_from_with_table("test_table") == exp.From(expressions=[exp.Table(this=exp.Identifier(this="test_table"))])

def test_query_create_from_expression_with_alias():
    assert create_from_with_table("test_table", "test_alias") == exp.From(expressions=[create_table_with_alias("test_table", "test_alias")])

def test_query_create_table_alias():
    assert create_table_with_alias("test_table", "test_alias") == exp.Alias(this=exp.Table(this=exp.Identifier(this="test_table")), alias=exp.TableAlias(this=exp.Identifier(this="test_alias")))

def test_query_create_where_with_condition():
    assert create_where_with_condition(exp.EQ(this=exp.Identifier(this="condition"))) == exp.Where(this=exp.EQ(this=exp.Identifier(this="condition")))

def test_query_create_star_selection():
    assert create_star_selection() == [exp.Star()]