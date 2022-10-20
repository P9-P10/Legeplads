from Helpers.Change import *

def test_change_constructor_sets_old_and_new_tuples():
    old_table, old_column = (Table('old_table'), Column('old_column'))
    new_table, new_column = (Table('new_table'), Column('new_column'))

    change = Change((old_table, old_column), (new_table, new_column))

    assert change.old == (old_table, old_column)
    assert change.new == (new_table, new_column)