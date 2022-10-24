from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column
from Helpers.Change import Change

def transform(query: Query, changes: list[Change], structure: list[Table]) -> Query:
    if structure:
        fully_qualify_column_names(query, query.tables_in_query(structure))
    apply_each_change(query, changes)

def fully_qualify_column_names(query, tables: list[Table]):
    query.create_needed_aliases()
    alias_map = create_alias_map(query)
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

def apply_each_change(query, changes):
    for change in changes:
        new_table = change.get_new_table()
        old_table = change.get_old_table()

        query.replace_table(old_table, new_table)
