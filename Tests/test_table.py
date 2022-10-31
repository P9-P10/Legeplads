from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column


def test_table_comparison_fails_if_other_is_not_table():
    assert not Table("name") == ["name"]


def test_table_comparison_succeeds_on_same_table_without_column():
    table1 = Table("name")
    table2 = Table("name")

    assert table1 == table2


def test_table_comparison_succeeds_on_same_table_with_same_columns():
    table1 = Table("name", [Column("col1"), Column("col2")])
    table2 = Table("name", [Column("col1"), Column("col2")])

    assert table1 == table2


def test_table_comparison_fails_on_table_with_different_name():
    table1 = Table("name")
    table2 = Table("other_name")

    assert not table1 == table2


def test_table_comparison_fails_on_table_with_different_columns():
    table1 = Table("name", [Column("col1"), Column("col2")])
    table2 = Table("name", [Column("col1"), Column("other_col2")])

    assert not table1 == table2


def test_table_comparison_succeeds_on_same_columns_in_different_order():
    table1 = Table("name", [Column("col1"), Column("col2")])
    table2 = Table("name", [Column("col2"), Column("col1")])

    assert table1 == table2


def test_table_has_column():
    table = Table("name", [Column("col1"), Column("col2")])
    assert table.has_column(Column("col1"))
    assert table.has_column(Column("col2"))
    assert not table.has_column(Column("col3"))
    assert not table.has_column(Column("no_such_column"))


def test_table_has_column_with_alias():
    column = Column("col1", "alias")
    table = Table("name", [Column("col1", "alias"), Column("col2")])

    assert table.has_column_with_alias(column, "alias")


def test_table_has_column_with_alias_fails_give_wrong_alias():
    column = Column("col1", "alias")
    table = Table("name", [Column("col1", "alias"), Column("col2")])

    assert not table.has_column_with_alias(column, "wrong_alias")


def test_alias():
    table = Table("name", [Column("col1"), Column("col2")])
    table.set_alias("alias")

    assert table.get_alias() == "alias"


def test_alias_defaults_none():
    table = Table("name", [Column("col1"), Column("col2")])

    assert table.get_alias() is None


def test_get_column():
    column2 = Column("col2")
    table = Table("name", [Column("col1"), column2])
    assert table.get_column("col2") == column2


def test_get_column_returns_none_if_column_not_in_columns():
    column2 = Column("col2")
    table = Table("name", [Column("col1"), column2])
    assert table.get_column("does_not_exist") is None

def test_copy_is_equal_to_original():
    original = Table("original", [Column("col1"), Column("col2")])
    copy = original.copy()

    assert copy == original

def test_copy_does_not_mutate_original():
    original = Table("original", [Column("col1"), Column("col2")])
    copy = original.copy()

    copy.set_alias("Copy")
    copy.columns.append(Column("col3"))

    assert copy.get_alias() == "Copy"
    assert original.get_alias() == None
    assert copy.columns == [Column("col1"), Column("col2"), Column("col3")]
    assert original.columns == [Column("col1"), Column("col2")]


def test_transform_creates_new_table_with_transform_applied():
    original = Table("original", [Column("col1"), Column("col2")])

    transformation1 = lambda table: table.set_alias("Org")
    transformation2 = lambda table: table.columns.append(Column("col3"))

    transformed_table_1 = original.transform(transformation1)
    transformed_table_2 = original.transform(transformation2)
    
    # only one instance should be affected by the transformation
    assert original.get_alias() == None
    assert transformed_table_1.get_alias() == "Org"
    assert transformed_table_2.get_alias() == None

    assert original.columns == [Column("col1"), Column("col2")]
    assert transformed_table_1.columns == [Column("col1"), Column("col2")]
    assert transformed_table_2.columns == [Column("col1"), Column("col2"), Column("col3")]

def test_transform_columns_creates_new_table_with_transform_applied_to_all_columns():
    original = Table("original", [Column("col1"), Column("col2")])
    transformation = lambda col: col.add_alias("Org")

    transformed_table = original.transform_columns(transformation)

    # Originals columns are not changed
    assert transformed_table.get_column("col1").get_alias() == "Org"
    assert transformed_table.get_column("col2").get_alias() == "Org"

    # Transformed tables columns are changed
    assert transformed_table.get_column("col1").get_alias() == "Org"
    assert transformed_table.get_column("col2").get_alias() == "Org"
