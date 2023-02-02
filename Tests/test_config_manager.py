import os
import pathlib
from os.path import exists

import pytest

from Helpers.config_manager import ConfigManager

@pytest.fixture
def test_file():
    """
    This fixture provides the filename as a parameter to the test.
    Once the test has completed, this fixture resumes control and removes the file.
    This ensures that no matter what happens in the test, the file is removed.
    """
    yield "NewFile"
    os.remove("NewFile")


def create_config_manager(path):
    correct_path = str(pathlib.Path(__file__).parent.parent / 'Tests') + "\\" + path
    return ConfigManager(correct_path)


def test_config_manager_init_file_does_not_exist_creates_file(test_file):
    ConfigManager(test_file)
    assert exists(test_file)


def test_config_manager_init_file_does_not_exist_creates_file_with_correct_content(test_file):
    with pytest.raises(ValueError) as v:
        cf = ConfigManager(test_file)
        cf.get_config()
    # This is impossible, as this is the function that raises an exception
    assert cf.config == {'changes_location': '', 'database_connections': [], 'database_versions_location': ''}
    assert "Please configure the config in" in str(v)
 

def test_config_manager_file_exists_loads_config():
    cf = create_config_manager("TestConfig.yml")
    assert cf.get_config() == {'changes_location': 'fancyLocation', 'database_versions_location': 'AnotherLocation'}
