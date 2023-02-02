import pytest
from Graph.changes_parser import ChangesParser
from Graph.graph_parser import GraphParser
from Graph.versionmanager import VersionManager
from Structures.Column import Column
from Structures.DataStore import DataStore
from Structures.Schema import Schema
from Structures.Table import Table


class Moc_GraphParser(GraphParser):
    def __init__(self):
        super().__init__()

    def get_structure(self, string_to_parse: str) -> list[DataStore]:
        return string_to_parse


class Moc_Changes_parser(ChangesParser):
    def __init__(self):
        super().__init__()

    def get_changes(self, old_structure: Schema, new_structure: Schema, changes: str):
        return changes


def create_version_manager(old_schema, new_schema):
    gp = Moc_GraphParser()
    cp = Moc_Changes_parser()

    old_ds = DataStore([old_schema], name="Name")
    new_ds = DataStore([new_schema], name="Name")
    old_tuple = (1, old_ds, "Id")
    new_tuple = (2, new_ds, "Id")
    parsed_change = [(old_schema, new_schema)]
    changes_tuple = (1, parsed_change, "Id")
    return VersionManager(gp, cp, [old_tuple, new_tuple], [changes_tuple])


@pytest.fixture
def old_schema():
    return Schema([Table("TableName", [Column("TestName", uri="1")])], name="SchemaName")

@pytest.fixture
def new_schema():
    return Schema([Table("TableName", [Column("NewColumnName", uri="2")])], name="SchemaName")


@pytest.fixture
def version_manager(old_schema, new_schema):
    return create_version_manager(old_schema, new_schema)



def test_init(old_schema, new_schema, version_manager):
    assert VersionManager.Change(1, old_schema, new_schema, "Id") in version_manager.changes


def test_get_changes_for_column(new_schema, version_manager):
    assert version_manager.get_change_for_column("TableName", "TestName", version=1, schema_name="SchemaName", ) == new_schema


def test_get_changes_for_column_wrong_value_returns_none(version_manager):
    assert version_manager.get_change_for_column("Non Existing", "Non Existing", version=1,
                                    schema_name="Non Existing") is None


def test_get_datastore_for_change(old_schema, new_schema, version_manager):
    old_ds = DataStore([old_schema], name="Name")
    new_ds = DataStore([new_schema], name="Name")

    result = version_manager.get_data_stores_for_change(version=1, database_id="Id")
    assert result == (old_ds, new_ds)
