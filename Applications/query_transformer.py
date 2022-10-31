from tokenize import Number
from Structures.Column import Column
from Structures.Query import Query
from Structures.Table import Table
from Structures.DatabaseStructure import DatabaseStructure
from Helpers.Change import Change
from Structures.QueryStructure import QueryStructure


def transform(query: Query, changes: list[Change], old_structure: list[Table], new_structure: list[Table]):
    old_structure = DatabaseStructure(old_structure)
    if query.has_star_expression():
        transform_star_expression(old_structure, query)

    new_changes = create_changes_to_transform_ambiguous_columns(query, changes, old_structure)
    all_changes = changes + new_changes
    apply_each_change(query, all_changes)


def transform_star_expression(old_structure: DatabaseStructure, query: Query):
    for table in query.get_tables():
        columns = old_structure.get_columns_in_table(table.name)
        transformation = prefix_transformation(table)
        columns_with_aliases = [column.transform(transformation) for column in columns]
        query.add_to_select(columns_with_aliases)

def prefix_transformation(table: Table):
    def fun(column: Column):
        alias = table.alias if table.alias else table.name
        column.add_alias(alias)
    return fun

def create_changes_to_transform_ambiguous_columns(query: Query, changes: list[Change], old_structure: DatabaseStructure):
    tables = query.get_tables()
    columns = query.get_columns()

    query_structure = QueryStructure(tables, columns)
    query_structure.resolve_columns(old_structure)

    def table_name_as_alias_transformation(column):
        column.alias = column.table_name

    columns_with_tables = [column.transform(table_name_as_alias_transformation) for column in query_structure.get_columns() if not column.alias]
    tables_after_changes = [apply_changes_to_table(table, changes) for table in tables]
    columns_with_new_tables = [apply_changes_to_column(column, changes) for column in columns_with_tables]
    
    ambiguous_columns = find_ambiguous_columns(columns_with_new_tables, tables_after_changes)
    resolved_columns = find_alias_for_ambiguous_columns(ambiguous_columns, columns_with_tables, tables)

    new_changes = create_changes_for_ambiguous_columns(ambiguous_columns, resolved_columns)
    return new_changes

def apply_changes_to_table(table: Table, changes: list[Change]) -> Table:
    new_table = get_new_table(table, changes)

    if new_table:
        changed_table = new_table.transform(add_alias_to_table_transformation(table.alias))
        return changed_table
    else:
        return table

def get_new_table(table: Table, changes: list[Change]) -> Change | None:
    for change in changes:
        if change.get_old_table() == table:
            return change.get_new_table()
    return None

def add_alias_to_table_transformation(table_alias):
    def fun(changed_table):
        changed_table.set_alias(changed_table.alias)
            # Keep the old alias if the change does not define a new alias
        if table_alias and not changed_table.alias:
            changed_table.set_alias(table_alias)
    return fun

def apply_changes_to_column(column: Column, changes: list[Change]) -> Column:
    change_for_column = get_change_for_column(column, changes)

    if change_for_column:
        # Copy the column from the change to avoid mutation
        changed_column = change_for_column.get_new_column().copy()
        add_alias_to_column(column, change_for_column, changed_column)
        return changed_column
    else:
        return column

def get_change_for_column(column: Column, changes: list[Change]) -> Change | None:
    for change in changes:
        if change.get_old_column() == column:
            return change
    return None

def add_alias_to_column(column: Column, change_for_column: Change, new_column: Column):
    # Keep the old alias if the change does not define a new alias
    if column.alias and not new_column.alias:
        new_column.add_alias(column.alias)

    # Add the new table name as alias if no other alias has been assigned
    if new_column.alias == change_for_column.get_old_table().name:
        table = change_for_column.get_new_table()
        new_column.add_alias(table.name)
        

def find_ambiguous_columns(columns: list[Column], tables: list[Table]) -> list[Column]:
    return [column for column in columns if column_occurs_in_multiple_tables(column, tables)]


def column_occurs_in_multiple_tables(column: Column, tables: list[Table]) -> int:
    count = 0
    for table in tables:
        if table.name == column.alias:
            count += 1
            if count > 1:
                return True
    return False


def find_alias_for_ambiguous_columns(columns: list[Column], columns_before_changes: list[Column],
                                     tables_before_changes: list[Table]) -> list[Column]:
    return [column_with_previous_alias(columns_before_changes, tables_before_changes, column) for column in columns]


def column_with_previous_alias(columns_before_changes, tables_before_changes, column):
    new_column = column.copy()
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
        create_change_for_adding_alias(col_with_table.alias, col_with_alias.name, col_with_alias.alias)
        for col_with_table, col_with_alias in zip(ambiguous_columns, resolved_columns)
    ]


def create_change_for_adding_alias(table_name, column_name, alias):
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
