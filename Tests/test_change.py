from Structures.Column import Column
from Structures.Table import Table
from Helpers.Change import *
import pytest

from Helpers.equality_constraint import EqualityConstraint


@pytest.fixture
def default_change():
    old_table, old_column = (Table('old_table'), Column('old_column'))
    new_table, new_column = (Table('new_table'), Column('new_column'))

    return Change((old_table, old_column), (new_table, new_column))


@pytest.fixture
def change_with_constraint():
    old_table, old_column = (Table('old_table'), Column('old_column'))
    new_table, new_column = (Table('new_table'), Column('new_column'))
    equality_constraint = EqualityConstraint(old_table, old_column, new_table, new_column)

    return Change((old_table, old_column), (new_table, new_column), equality_constraint)


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


def test_get_constraint(change_with_constraint):
    old_table, old_column = (Table('old_table'), Column('old_column'))
    new_table, new_column = (Table('new_table'), Column('new_column'))
    equality_constraint = EqualityConstraint(old_table, old_column, new_table, new_column)

    assert change_with_constraint.get_constraint() == equality_constraint

def test_table_changed_false_if_no_change():
    old = (Table('old_table'), Column('old_column'))
    new = (Table('old_table'), Column('new_column'))

    assert Change(old, new).table_changed() == False


def test_table_changed_true_if_change():
    old = (Table('old_table'), Column('old_column'))
    new = (Table('new_table'), Column('new_column'))

    assert Change(old, new).table_changed() == True


def test_column_changed_false_if_not_changed():
    old = (Table('old_table'), Column('old_column'))
    new = (Table('new_table'), Column('old_column'))

    assert Change(old, new).column_changed() == False

def test_column_changed_true_if_changed():
    old = (Table('old_table'), Column('old_column'))
    new = (Table('new_table'), Column('new_column'))

    assert Change(old, new).column_changed() == True