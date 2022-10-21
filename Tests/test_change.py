from Applications.DatabaseRepresenations.Column import Column
from Applications.DatabaseRepresenations.Table import Table
from Helpers.Change import *
import pytest


@pytest.fixture
def default_change():
    old_table, old_column = (Table('old_table'), Column('old_column'))
    new_table, new_column = (Table('new_table'), Column('new_column'))

    return Change((old_table, old_column), (new_table, new_column))

def test_change_constructor_sets_old_and_new_tuples():
    old_table, old_column = (Table('old_table'), Column('old_column'))
    new_table, new_column = (Table('new_table'), Column('new_column'))

    change = Change((old_table, old_column), (new_table, new_column))

    assert change.old == (old_table, old_column)
    assert change.new == (new_table, new_column)

def test_change_get_old_table(default_change):
    assert default_change.get_old_table() == Table('old_table')

def test_change_get_new_table(default_change):
    assert default_change.get_new_table() == Table('new_table')

def test_change_get_old_column(default_change):
    assert default_change.get_old_column() == Column('old_column')

def test_change_get_new_column(default_change):
    assert default_change.get_new_column() == Column('new_column')