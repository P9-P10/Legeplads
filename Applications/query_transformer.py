from tokenize import Number
from Applications.DatabaseRepresenations.Column import Column
from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Helpers.Change import Change


def transform(query: Query, changes: list[Change], old_structure: list[Table], new_structure: list[Table]):
    tables = query.get_tables()
    columns = query.get_columns()

    columns_with_tables = resolve_columns_without_alias(columns, old_structure)

    tables_after_changes = [apply_changes_to_table(table, changes) for table in tables]

    columns_with_new_tables = [apply_changes_to_column(column, changes) for column in columns_with_tables]

    ambiguous_columns = find_ambiguous_columns(columns_with_new_tables, tables_after_changes)
    resolved_columns = find_alias_for_ambiguous_columns(ambiguous_columns, columns_with_tables, tables)

    new_changes = create_changes_for_ambiguous_columns(ambiguous_columns, resolved_columns)
    all_changes = changes + new_changes
    apply_each_change(query, all_changes)


def resolve_columns_without_alias(columns: list[Column], tables: list[Table]) -> list[Column]:
    # This function requires that there are no ambiguous columns in the input query
    columns_without_alias = [column for column in columns if not column.alias]
    return [create_column_with_table_alias(tables, column) for column in columns_without_alias]

def create_column_with_table_alias(tables, column):
    new_column = Column(column.name)
    table = find_table_for_column(column, tables)
    if table:
        new_column.add_alias(table.name)
    return new_column

def find_table_for_column(column: Column, tables: list[Table]) -> Table:
    for table in tables:
        if table.has_column(column):
            return table
    # Should perhaps throw exception, as there should always be a table for every column in the query
    return None


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

        # Add the new table name as alias if no other alias has been assigned
        if new_column.alias == change_for_column.get_old_table().name:
            table = change_for_column.get_new_table()
            new_column.add_alias(table.name)
        return new_column
    else:
        return column

def get_change_for_column(column: Column, changes: list[Change]) -> Change | None:
    for change in changes:
        if change.get_old_column() == column:
            return change
    return None

def find_ambiguous_columns(columns: list[Column], tables: list[Table]) -> list[Column]:
    return [column for column in columns if count_tables_containing_column(column, tables) > 1]

def count_tables_containing_column(column: Column, tables: list[Table]) -> int:
    count = 0
    for table in tables:
        if table.name == column.alias:
            count += 1
    return count

def find_alias_for_ambiguous_columns(columns: list[Column], columns_before_changes: list[Column], tables_before_changes: list[Table]) -> list[Column]:
    return [column_with_previous_alias(columns_before_changes, tables_before_changes, column) for column in columns]

def column_with_previous_alias(columns_before_changes, tables_before_changes, column):
    new_column = Column(column.name, column.alias)
    alias_before_changes = get_previous_alias(column, columns_before_changes, tables_before_changes)
    if alias_before_changes:
        new_column.add_alias(alias_before_changes)
    return new_column

def get_previous_alias(column: Column, columns_before_changes: list[Column], tables_before_changes: list[Table]) -> str:
    previous_table_name = get_previous_table(column, columns_before_changes)
    return get_alias_for_table(previous_table_name, tables_before_changes)


def get_previous_table(column, columns_before_changes):
    for old_column in columns_before_changes:
        if old_column.name == column.name:
            return old_column.alias

def get_alias_for_table(table_name: str, tables: list[Table]) -> str:
    for table in tables:
        if table.name == table_name:
            return table.alias
    return None

def create_changes_for_ambiguous_columns(ambiguous_columns, resolved_columns):
    return [
        create_change_for_resolving_ambiguity(col_with_table, col_with_alias) 
        for col_with_table, col_with_alias in zip(ambiguous_columns, resolved_columns)
    ]

def create_change_for_resolving_ambiguity(col_with_table, col_with_alias):
    table_name = col_with_table.alias
    alias = col_with_alias.alias
    column_name = col_with_alias.name
    return Change((Table(table_name), Column(column_name)), (Table(table_name), Column(column_name, alias)))

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
   
