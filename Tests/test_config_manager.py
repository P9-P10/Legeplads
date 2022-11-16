import os
import pathlib
from os.path import exists

import pytest

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
    try:
        cf = ConfigManager(file_path)
    except ValueError:
        assert cf.get_config() == {'changes_location': '', 'database_versions_location': ''}
        assert "Please configure the config in" in v.value
    finally:
        os.remove(file_path)


def test_config_manager_file_exists_loads_config():
    cf = create_config_manager("TestConfig.yml")
    assert cf.get_config() == {'changes_location': 'fancyLocation', 'database_versions_location': 'AnotherLocation'}
