from http.client import ImproperConnectionState
from Applications.optimizedSqlInterface import OptimizedSqliteInterface as OSi
from Helpers.changes_class import Changes as Ch
from Applications.sqliteinterface import DBConfig

def test_modify_query_with_change_remove_value():
    connection = OSi(DBConfig(""))
    connection.add_database_change('other_table', Ch())
    query = "SELECT name, ot.other_value FROM testTable JOIN other_table ot"
    result = connection.modify_query_with_changes(query)
    assert result == "SELECT name, other_value FROM testTable"


def test_modify_query_with_change_replace_value():
    connection = OSi(DBConfig(""))
    connection.add_database_change('other_table', Ch(new_name="correct_table"))
    query = "SELECT name, ot.other_value FROM testTable JOIN other_table ot"
    result = connection.modify_query_with_changes(query)
    assert result == "SELECT name, ot.other_value FROM testTable JOIN correct_table ot"
