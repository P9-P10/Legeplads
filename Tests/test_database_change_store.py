from Helpers.Change import TableChange
from Helpers.database_change_store import DatabaseChangeStore


def test_get_changes_initially_returns_empty_list():
    change_store = DatabaseChangeStore()
    assert change_store.get_changes() == []


def test_get_changes_returns_list_with_element():
    change_store = DatabaseChangeStore()
    change_store.add_new_change(TableChange("Table",[]))
    assert change_store.get_changes() != []


def test_get_changes_returns_specific_element():
    change_store = DatabaseChangeStore()
    change = TableChange("name",[])
    change_store.add_new_change(change)
    assert change in change_store.get_changes()
