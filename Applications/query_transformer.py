from Applications.DatabaseRepresenations.Column import Column
from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Helpers.Change import Change


def transform(query: Query, changes: list[Change], old_structure: list[Table], new_structure: list[Table]):
    tables = query.get_tables()
    columns = query.get_columns()

    tables_after_changes = [apply_changes_to_table(table, changes) for table in tables]
    columns_after_changes = [apply_changes_to_column(column, changes) for column in columns]

    # if any column without a prefix in columns_after_changes occurs in multiple tables in new_structure
    # if of the tables is missing a prefix, create one for it
    # add the prefix for the appropiate table to the column

    apply_each_change(query, changes)

def apply_changes_to_table(table: Table, changes: list[Change]) -> Table:
    change_for_table = get_change_for_table(table, changes)

    if change_for_table:
        # Copy the table from change to avoid mutation
        changed_table = change_for_table.get_new_table()
        new_table = Table(changed_table.name, changed_table.columns)
        new_table.set_alias(changed_table.alias)
        # Keep the old alias if the change does not define a new alias
        if table.alias and not new_table.alias:
            new_table.set_alias(table.alias)
        return new_table
    else:
        return table

def get_change_for_table(table: Table, changes: list[Change]) -> Change | None:
    for change in changes:
        if change.get_old_table() == table:
            return change
    return None

def apply_changes_to_column(column: Column, changes: list[Change]) -> Column:
    change_for_column = get_change_for_column(column, changes)

    if change_for_column:
        # Copy the column from the change to avoid mutation
        changed_column = change_for_column.get_new_column()
        new_column = Column(changed_column.name, changed_column.alias)
        # Keep the old alias if the change does not define a new alias
        if column.alias and not new_column.alias:
            new_column.add_alias(column.alias)
        return new_column
    else:
        return column

def get_change_for_column(column: Column, changes: list[Change]) -> Change | None:
    for change in changes:
        if change.get_old_column() == column:
            return change
    return None

def apply_each_change(query, changes):
    for change in changes:
        new_table = change.get_new_table()
        new_column = change.get_new_column()
        old_table = change.get_old_table()
        old_column = change.get_old_column()
        constraint = change.get_constraint()

        query.replace_table(old_table, new_table)
        query.replace_column(old_column, new_column)
        
        if constraint:
            query.replace_matching_identifers(constraint.left_column.name, constraint.right_column.name)
   
