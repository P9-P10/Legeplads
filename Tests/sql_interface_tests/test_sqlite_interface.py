import pytest

from Applications.Database_intefaces.sqliteinterface import SqLiteInterface, DBConfig

database_name = "DoesNotExist"


def create_sqlite_interface_which_does_not_exist():
    return SqLiteInterface(DBConfig(database_name))


def test_sqlite_raises_file_not_found_when_given_not_existing_file():
    with pytest.raises(FileNotFoundError):
        create_sqlite_interface_which_does_not_exist()