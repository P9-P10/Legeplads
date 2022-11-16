import json

from Graph.sql_lite_changes_parser import JsonChangesParser
from Structures.Column import Column
from Structures.DataStore import DataStore
from Structures.Schema import Schema
from Structures.Table import Table


def test__get_changes_move_columns_action():
    changes = ['MOVE(123456789,852852852)']
    changes = json.dumps(changes)
    changes_parser = JsonChangesParser(changes)
    old_db_structure = DataStore([Schema([Table("TableNameA", [Column("name", uri=123456789)], uri=852852)],
                                         uri=963963)])
    new_db_structure = DataStore([Schema([Table("TableNameB", [Column("second_name", uri=852852852)], uri=123456963)],
                                         uri=852789456123)])
    changes = changes_parser.get_changes(old_db_structure, new_db_structure)
    assert changes == [(Schema([Table("TableNameA", [Column("name")])]),
                        Schema([Table("TableNameB", [Column("second_name")])]))]


def test_get_changes_multiple_move_columns_actions():
    changes = ['MOVE(123456789,852852852)', 'MOVE(5252,8989)']
    changes = json.dumps(changes)
    changes_parser = JsonChangesParser(changes)
    old_db_structure = DataStore([Schema(
        [Table("TableNameA", [Column("name", uri=123456789),
                              Column("ColumnC", uri=5252)], uri=852852)],
        uri=963963)])
    new_db_structure = DataStore([Schema([Table("TableNameB",
                                                [Column("second_name", uri=852852852)], uri=123456963),
                                          Table("tableA",
                                                [Column("ColumnC", uri=8989)])], uri=852789456123)])
    changes = changes_parser.get_changes(old_db_structure, new_db_structure)
    first_tuple = (Schema([Table("TableNameA", [Column("name")])]),
                   Schema([Table("TableNameB", [Column("second_name")])]))
    second_tuple = (Schema([Table("TableNameA", [Column("ColumnC")])]),
                    Schema([Table("tableA", [Column("ColumnC")])]))
    assert changes == [first_tuple, second_tuple]


def test_get_changes_move_table_to_new_schema():
    changes = ['MOVE(1,11)']
    changes = json.dumps(changes)
    changes_parser = JsonChangesParser(changes)
    schema_one = Schema(
        [Table("a", columns=[
            Column("a1", uri=4),
            Column("a2", uri=5)], uri=1),
         Table("B", columns=[
             Column("B1", uri=3),
             Column("B2", uri=6)], uri=2)
         ], name="One")
    schema_two = Schema(
        [Table("a", columns=[
            Column("a1", uri=7),
            Column("a2", uri=8)], uri=9)], name="Two")

    schema_three = Schema(
        [Table("a", columns=[
            Column("a1", uri=7),
            Column("a2", uri=8)], uri=9),
         Table("q", uri=11)], name="Three")
    old_db_structure = DataStore([schema_one, schema_two])
    new_db_structure = DataStore([schema_three])
    changes = changes_parser.get_changes(old_db_structure, new_db_structure)
    old, new = changes[0]
    assert old.tables[0].name == "a" and new.tables[0].name == "q"
    assert old.name == "One" and new.name == "Three"
