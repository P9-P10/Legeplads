import pytest

from Applications.Database_intefaces.sqliteinterface import SqLiteInterface
from Tests.test_helpers.DBConfig import DBConfig

database_name = "DoesNotExist"
db_conf = DBConfig(database_name)


def create_sqlite_interface_which_does_not_exist():
    return SqLiteInterface(db_conf.get_path_to_database())


def test_sqlite_raises_file_not_found_when_given_not_existing_file():
    with pytest.raises(FileNotFoundError):
        create_sqlite_interface_which_does_not_exist()