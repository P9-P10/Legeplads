import os
import pathlib
from os.path import exists

from Helpers.config_manager import ConfigManager


def create_config_manager(path):
    correct_path = str(pathlib.Path(__file__).parent.parent / 'Tests') + "\\" + path
    return ConfigManager(correct_path)


def test_config_manager_init_file_does_not_exist_creates_file():
    file_path = "NewFile"
    cf = ConfigManager(file_path)
    assert exists(file_path)
    os.remove(file_path)


def test_config_manager_init_file_does_not_exist_creates_file_with_correct_content():
    file_path = "NewFile"
    cf = ConfigManager(file_path)
    assert cf.get_config() == {'changes_location': '', 'database_versions_location': ''}
    os.remove(file_path)


def test_config_manager_file_exists_loads_config():
    cf = create_config_manager("TestConfig.yml")
    assert cf.get_config() == {'changes_location': 'fancyLocation', 'database_versions_location': 'AnotherLocation'}
