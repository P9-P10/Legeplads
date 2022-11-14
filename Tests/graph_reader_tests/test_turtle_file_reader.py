import pathlib

from Helpers.filereader import FileReader
from Graph.turtle_parser import TurtleParser
from Structures.Column import Column
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Table import Table


def create_turtle_reader(path):
    correct_path = str(pathlib.Path(__file__).parent.parent.parent / 'Tests' / 'graph_reader_tests') + '\\' + path
    file_reader = FileReader(correct_path)
    return TurtleParser(file_reader.get_content())


def find_database_structure_in_result(result: [DatabaseStructure], query) -> DatabaseStructure:
    items = [item for item in result if item.name == query]
    return items[0]


def tables_in_database(result, database_name, tables):
    current_database = find_database_structure_in_result(result, database_name)
    # As the parser is nondeterministic, it is necessary to verify whether all tables are present
    return all([item in tables for item in current_database.tables]) and all(
        [item in current_database.tables for item in tables])


expected_tables_optimized_advanced_database = [
    Table("Orders", [Column("owner"), Column("product"), Column("quantity"), Column("id"),
                     Column("order_time")]),
    Table("RecoveryQuestions", [Column("user_id"), Column("answer"), Column("question")]),
    Table("Users",
          [Column("email"), Column("password"), Column("creation_date"), Column("id")]),
    Table("Products", [Column("name"), Column("product_id")]),
    Table("UserData",
          [Column("wants_letter"), Column("birthday"), Column("user_id"), Column("phone"),
           Column("name"),
           Column("id"), Column("address")])]

expected_tables_simple_database = [
    Table("UserData", [Column("phone"), Column("birthday"), Column("address"), Column("id")]),
    Table("Users", [Column("email"), Column("id"), Column("password")])]


def test_get_structure_returns_data_base_structure():
    turtle_reader = create_turtle_reader("file_for_tests.ttl")
    result = turtle_reader.get_structure()
    expected = [Table("table", [Column("AnotherName")])]
    assert result[0].tables == expected
    assert result[0].name == "TestDatabase"


def test_get_structure_returns_database_structure_multiple_tables():
    turtle_reader = create_turtle_reader("larger_file.ttl")
    result = turtle_reader.get_structure()
    assert len(result) == 1
    assert len(result[0].tables) == 5


def test_get_structure_returns_database_structure_correct_tables():
    turtle_reader = create_turtle_reader("larger_file.ttl")
    result = turtle_reader.get_structure()

    assert tables_in_database(result, "OptimizedAdvancedDatabase", expected_tables_optimized_advanced_database)


def test_get_structure_multiple_database_structures_returns_correct_structures():
    turtle_reader = create_turtle_reader("large_file_with_two_databases.ttl")
    result = turtle_reader.get_structure()
    optimized_database_name = "OptimizedAdvancedDatabase"
    simple_database_name = "SimpleDatabase"

    # Checks if there are no duplicate database entries
    assert len([item for item in result if item.name == optimized_database_name]) == 1
    assert len([item for item in result if item.name == simple_database_name]) == 1
    # Checks that the database entries contains the correct tables.
    assert tables_in_database(result, optimized_database_name, expected_tables_optimized_advanced_database)
    assert tables_in_database(result, simple_database_name, expected_tables_simple_database)
