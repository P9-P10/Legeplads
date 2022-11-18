import json

from Graph.json_changes_parser import JsonChangesParser
from Structures.Column import Column
from Structures.DataStore import DataStore
from Structures.Schema import Schema
from Structures.Table import Table


def test__get_changes_move_columns_action():
    changes = ['MOVE(123456789,852852852)']
    changes = json.dumps(changes)
    changes_parser = JsonChangesParser()
    old_db_structure = DataStore([Schema([Table("TableNameA", [Column("name", uri="123456789")], uri="852852")],
                                         uri="963963")])
    new_db_structure = DataStore([Schema([Table("TableNameB", [Column("second_name", uri="852852852")], uri="123456963")],
                                         uri="852789456123")])
    changes = changes_parser.get_changes(old_db_structure, new_db_structure,changes)
    assert changes == [(Schema([Table("TableNameA", [Column("name")])]),
                        Schema([Table("TableNameB", [Column("second_name")])]))]


def test_get_changes_multiple_move_columns_actions():
    changes = ['MOVE(123456789,852852852)', 'MOVE(5252,8989)']
    changes = json.dumps(changes)
    changes_parser = JsonChangesParser()
    old_db_structure = DataStore([Schema(
        [Table("TableNameA", [Column("name", uri="123456789"),
                              Column("ColumnC", uri="5252")], uri="852852")],
        uri="963963")])
    new_db_structure = DataStore([Schema([Table("TableNameB",
                                                [Column("second_name", uri="852852852")], uri="123456963"),
                                          Table("tableA",
                                                [Column("ColumnC", uri="8989")])], uri="852789456123")])
    changes = changes_parser.get_changes(old_db_structure, new_db_structure,changes)
    first_tuple = (Schema([Table("TableNameA", [Column("name")])]),
                   Schema([Table("TableNameB", [Column("second_name")])]))
    second_tuple = (Schema([Table("TableNameA", [Column("ColumnC")])]),
                    Schema([Table("tableA", [Column("ColumnC")])]))
    assert changes == [first_tuple, second_tuple]

