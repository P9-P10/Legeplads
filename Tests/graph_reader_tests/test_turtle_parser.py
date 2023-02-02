import pathlib

from Helpers.filereader import FileReader
from Graph.turtle_parser import TurtleParser
from Structures.Column import Column
from Structures.DataStore import DataStore
from Structures.Schema import Schema
from Structures.Table import Table


def get_file_contents(path):
    correct_path = str(pathlib.Path(__file__).parent.parent.parent / 'Tests' / 'graph_reader_tests') + '\\' + path
    file_reader = FileReader(correct_path)
    return file_reader.get_content()


def find_schema_structure_in_datastore(result: list[DataStore], query, schema_name="main") -> Schema:
    result = [schema for schema in result.schemas if schema.name == schema_name]
    return result[0]


def tables_in_database(result, database_name, tables):
    current_database = find_schema_structure_in_datastore(result, database_name)
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
    turtle_reader = TurtleParser()
    result = turtle_reader.get_structure(get_file_contents("file_for_tests.ttl"))
    expected = [Table("table", [Column("AnotherName")])]
    assert result.schemas[0].tables == expected
    assert result.name == "TestDatabase"


def test_get_structure_returns_database_structure_multiple_schemas():
    turtle_reader = TurtleParser()
    result = turtle_reader.get_structure(get_file_contents("large_file_multiple_schemas.ttl"))
    assert len(result.schemas) == 2
    assert len([schema for schema in result.schemas if schema.name == "main"]) == 1
    assert len([schema for schema in result.schemas if schema.name == "secondmain"]) == 1


def test_get_structure_returns_database_structure_correct_tables():
    turtle_reader = TurtleParser()
    result = turtle_reader.get_structure(get_file_contents("larger_file.ttl"))

    assert tables_in_database(result, "OptimizedAdvancedDatabase", expected_tables_optimized_advanced_database)
