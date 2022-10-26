from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Helpers.Change import Change


def transform(query: Query, changes: list[Change], old_structure: list[Table], new_structure: list[Table]):
    query.create_needed_aliases()
    alias_map = create_alias_map(query)

    if new_structure:
        fully_qualify_column_names(query, query.tables_in_query(new_structure), alias_map)

    if old_structure:
        fully_qualify_column_names(query, query.tables_in_query(old_structure), alias_map)

    apply_each_change(query, changes, alias_map)


def fully_qualify_column_names(query, tables: list[Table], alias_map):
    if len(alias_map) > 0:
        query.apply_missing_aliases(tables, alias_map)


def create_alias_map(query):
    alias_map = {}
    for alias in query.get_aliases():
        add_alias_if_exists(query, alias, alias_map)
    return alias_map


def add_alias_if_exists(query, alias, alias_map):
    table = query.get_table(alias)
    if table:
        add_alias(query, alias, alias_map, table)


def add_alias(query, alias, alias_map, table):
    table_alias = query.get_table_alias(alias)
    alias_map[table.name] = table_alias.name


def apply_each_change(query, changes, alias_map):
    for change in changes:
        new_table = change.get_new_table()
        old_table = change.get_old_table()

        query.replace_table(old_table, new_table)
        constraint = change.get_constraint()
        if constraint:
            query.change_column_in_comparisons(alias_map.get(str(old_table)),
                                               old_column=constraint.left_column,
                                               new_column=constraint.right_column)
