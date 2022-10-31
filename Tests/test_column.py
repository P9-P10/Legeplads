from Structures.Column import Column
from Applications.query_transformer import transform


def test_column_comparison_fails_if_other_is_not_column():
    assert not Column("name") == ["name"]


def test_column_comparison_succeeds_on_same_column_names():
    column1 = Column("name")
    column2 = Column("name")

    assert column1 == column2


def test_column_comparison_fails_on_different_column_names():
    column1 = Column("name")
    column2 = Column("other_name")

    assert not column1 == column2

def test_alias_defualts_none():
    column = Column("Name")
    assert column.get_alias() is None


def test_alias():
    column = Column("Name")
    column.add_alias("Alias")

    assert column.get_alias() == "Alias"

def test_copy_is_equal_to_original():
    original = Column("Column", "Col")
    copy = original.copy()

    assert copy == original

def test_copy_does_not_mutate_original():
    original = Column("Original", "Org")
    copy = original.copy()

    copy.add_alias("Copy")

    assert copy.get_alias() == "Copy"
    assert original.get_alias() == "Org"

def test_transform_creates_new_column_with_transform_applied():
    original = Column("Original")
    transformation = lambda col: col.add_alias("Org")

    transformed_column = original.transform(transformation)

    assert transformed_column.get_alias() == "Org"
    assert original.get_alias() == None