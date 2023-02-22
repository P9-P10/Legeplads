from Graph.changes_graph_parser import *
from Structures.Column import Column
from Structures.Table import Table


def test_get_changes_from_graph():
    parser = ChangesGraphParser()
    old_structure = DataStore([Schema([Table("TableNameA", [Column("name", uri="123456789")], uri="852852")],
                                      uri="963963")])
    new_structure = DataStore([Schema([Table("TableNameB", [Column("second_name", uri="852852852")], uri="123456963")],
                                      uri="852789456123")])
    changes = '[["move1","123456963","852852","name",["where X = Y"],"false"],["move1","dest","src","column","cond","default"]]'
    parsed_changes = parser.get_changes(old_structure, new_structure, changes)
    assert parsed_changes == [
        (Schema([Table("TableNameA", [Column("name")])]),
         Schema([Table("TableNameB", [Column("name")])]))
    ]
