import pathlib

import pytest

from Helpers.filereader import FileReader


def create_file_reader(path):
    correct_path = str(pathlib.Path(__file__).parent.parent.parent / 'Tests' / 'graph_reader_tests') + '\\' + path
    return FileReader(correct_path)


def test_init_raises_file_not_found_on_incorrect_file_path():
    with pytest.raises(FileNotFoundError):
        create_file_reader("Incorrect filepath")


def test_init_does_not_raise_error_if_file_exists():
    file_reader = create_file_reader("file_for_tests.ttl")
    assert "file_for_tests.ttl" in file_reader.location
