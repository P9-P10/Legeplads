from Applications.DatabaseRepresenations.Column import Column
from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Helpers.Change import Change


def transform(query: Query, changes: list[Change], old_structure: list[Table], new_structure: list[Table]):
    tables = query.get_tables()
    columns = query.get_columns()
    apply_each_change(query, changes)


def apply_each_change(query, changes):
    for change in changes:
        new_table = change.get_new_table()
        new_column = change.get_new_column()
        old_table = change.get_old_table()
        old_column = change.get_old_column()

        query.replace_table(old_table, new_table)
        query.replace_column(old_column, new_column)
        apply_constraints(query, change, new_table)

def apply_constraints(query, change, old_table):
    constraint = change.get_constraint()
    if constraint:
        query.change_column_in_comparisons(str(old_table),
                                           old_column=constraint.left_column,
                                           new_column=constraint.right_column)
