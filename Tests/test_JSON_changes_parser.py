import json

from Graph.sql_lite_changes_parser import JsonChangesParser
from Structures.Column import Column
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Table import Table


def test__get_changes_move_action():
    changes = ['MOVE(123456789,852852852)']
    changes = json.dumps(changes)
    changes_parser = JsonChangesParser(changes)
    old_db_structure = DatabaseStructure([Table("TableNameA", [Column("name", uri=123456789)], uri="852852")],
                                         uri=963963)
    new_db_structure = DatabaseStructure([Table("TableNameB", [Column("second_name", uri=852852852)], uri="123456963")],
                                         uri=852789456123)
    changes = changes_parser.get_changes(old_db_structure, new_db_structure)
    assert changes == [(Table("TableNameA", [Column("name")]),
                        Table("TableNameB", [Column("second_name")]))]


def test_get_changes_multiple_move_actions():
    changes = ['MOVE(123456789,852852852)', 'MOVE(5252,8989)']
    changes = json.dumps(changes)
    changes_parser = JsonChangesParser(changes)
    old_db_structure = DatabaseStructure(
        [Table("TableNameA", [Column("name", uri=123456789),
                              Column("ColumnC", uri=5252)], uri="852852")],
        uri=963963)
    new_db_structure = DatabaseStructure([Table("TableNameB",
                                                [Column("second_name", uri=852852852)], uri="123456963"),
                                          Table("tableA",
                                                [Column("ColumnC", uri=8989)])], uri=852789456123)
    changes = changes_parser.get_changes(old_db_structure, new_db_structure)
    first_tuple = (Table("TableNameA", [Column("name")]),
                   Table("TableNameB", [Column("second_name")]))
    second_tuple = (Table("TableNameA", [Column("ColumnC")]),
                    Table("tableA", [Column("ColumnC")]))
    assert changes == [first_tuple, second_tuple]
