from Helpers.Change import *


def test_table_change_init_properties_set():
    table_change = TableChange("name", [])
    assert table_change.old_name == "name"


def test_get_column_changes_from_table_change():
    table = Table("name")
    input_colmn_changes = [ColumnChange("old_name", "new_name", new_table=table)]
    table_change = TableChange("name", input_colmn_changes)
    column_changes = table_change.get_column_changes()
    assert column_changes == input_colmn_changes


def test_column_change_init_properties_set():
    table = Table("name")
    change = ColumnChange(old_name="test_name", new_name="new_test_name", new_table=table)
    assert change.old_name == "test_name"
    assert change.new_name == "new_test_name"
    assert change.new_table == table
