from Structures.Relation import Relation, Attribute
from Structures.Table import Table
from Structures.Column import Column

def test_relation_get_name_returns_name_of_table():
    table = Table("table_name")
    relation = Relation(None, table, None)

    assert relation.get_name() == "table_name"


def test_relation_change_table_changes_the_table():
    table_one = Table("table_one")
    table_two = Table("table_two")

    relation = Relation(None, table_one, None)

    assert relation.get_name() == "table_one"
    relation.change_table(table_two)
    assert relation.get_name() == "table_two"


def test_attribute_get_name_returns_name_of_column():
    column = Column("column_name")
    attribute = Attribute(None, column)

    assert attribute.get_name() == "column_name"

def test_attribute_change_column_changes_the_column():
    column_one = Column("column_one")
    column_two = Column("column_two")

    attribute = Attribute(None, column_one)

    assert attribute.get_name() == "column_one"
    attribute.change_column(column_two)
    assert attribute.get_name() == "column_two"