from venv import create
from Structures.Node import EntityNode, TableNode, ColumnNode
import pytest
from sqlglot import exp

def test_entity_node_get_name():
    node = EntityNode(None, "node_name")
    assert node.get_name() == "node_name"

def test_entity_node_set_name_changes_name():
    node = EntityNode(None, "name")
    node.set_name("other_name")
    assert node.get_name() == "other_name"

def test_entity_node_set_alias_sets_alias():
    node = EntityNode(None, "name", None)
    node.set_alias("alias")
    assert node.get_alias() == "alias"


def test_entity_node_has_alias():
    node_without_alias = EntityNode(None, "no_alias")
    node_with_alias = EntityNode(None, "yes_alias", "yes")

    assert node_without_alias.has_alias() == False
    assert node_with_alias.has_alias() == True


def test_entity_node_get_alias():
    node_with_alias = EntityNode(None, "yes_alias", "yes")
    assert node_with_alias.get_alias() == "yes"

    
def test_entity_node_get_alias_throws_if_no_alias():
    node_without_alias = EntityNode(None, "no_alias")

    with pytest.raises(AttributeError):
        node_without_alias.get_alias()

def test_entity_node_get_query_node_returns_the_same_object():
    # This is tested with a mutable type, so that the paramter is passed by reference
    mock_query_node = ["query_node"]
    node = EntityNode(mock_query_node, "name")

    assert node.get_query_node() is mock_query_node


# Taken from Structures/Query
# Move to separate module for handling nodes or expression trees
def create_column(name, table=None):
    if table:
        return exp.Column(
            this=create_identifier(name),
            table=create_identifier(table)
        )
    else:
        return exp.Column(this=create_identifier(name))


def create_identifier(name: str):
    return exp.Identifier(this=name)


def create_table(name, alias=None):
    if alias:
        return exp.Alias(this=create_table(name), alias=exp.TableAlias(this=create_identifier(alias)))
    else:
        return exp.Table(this=create_identifier(name))


def test_column_node_defines_name_given_query_node_without_alias():
    query_column = create_column("test_column")
    column_node = ColumnNode(query_column)

    assert column_node.get_name() == "test_column"
    assert column_node.has_alias() == False


def test_column_node_defines_name_and_alias_given_query_node_with_alias():
    query_column = create_column("test_column", "alias")
    column_node = ColumnNode(query_column)

    assert column_node.get_name() == "test_column"
    assert column_node.has_alias() == True
    assert column_node.get_alias() == "alias"


def test_column_node_create_new_query_node_without_alias():
    query_column = create_column("test_column")
    column_node = ColumnNode(query_column)
    
    assert column_node.create_new_query_node() == create_column("test_column")


def test_column_node_create_new_query_node_with_alias():
    query_column = create_column("test_column", "alias")
    column_node = ColumnNode(query_column)
    
    assert column_node.create_new_query_node() == create_column("test_column", "alias")


def test_column_node_set_name_changes_name_of_produced_query_node():
    query_column = create_column("test_column", "alias")
    column_node = ColumnNode(query_column)
    column_node.set_name("other_column")
    
    assert column_node.create_new_query_node() == create_column("other_column", "alias")

# This test is just to verify that comparison of classes from sqlglot behaved as expected
def test_query_node_comparison_fail_if_alias_does_not_match():
    query_column = create_column("test_column", "alias")
    column_node = ColumnNode(query_column)
    
    assert not column_node.create_new_query_node() == create_column("test_column")

def test_query_node_throws_if_not_given_correct_query_node_type():
    # This test is by no means exhaustive, but tests that the type of the input is checked
    with pytest.raises(TypeError):
        ColumnNode(["this", "is", "not", "a", "column"])

def test_table_node_defines_name_given_query_node_without_alias():
    query_table = create_table("test_table")
    table_node = TableNode(query_table)

    assert table_node.get_name() == "test_table"
    assert table_node.has_alias() == False


def test_table_node_defines_name_and_alias_given_query_node_with_alias():
    query_table = create_table("test_table", "alias")
    table_node = TableNode(query_table)

    assert table_node.get_name() == "test_table"
    assert table_node.has_alias() == True
    assert table_node.get_alias() == "alias"


def test_table_node_create_new_query_node_without_alias():
    query_table = create_table("test_table")
    table_node = TableNode(query_table)
    
    assert table_node.create_new_query_node() == create_table("test_table")


def test_table_node_create_new_query_node_with_alias():
    query_table = create_table("test_table", "alias")
    table_node = TableNode(query_table)
    
    assert table_node.create_new_query_node() == create_table("test_table", "alias")


def test_table_node_throws_if_not_given_correct_query_node_type():
    with pytest.raises(TypeError):
        TableNode(["this", "is", "not", "a", "table"])


def test_table_node_set_name_changes_name_of_produced_query_node():
    query_table = create_table("test_table", "alias")
    table_node = TableNode(query_table)
    table_node.set_name("other_table")
    
    assert table_node.create_new_query_node() == create_table("other_table", "alias")