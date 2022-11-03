from audioop import add
from tokenize import Number
from Structures.Column import Column
from Structures.Query import Query
from Structures.Table import Table
from Structures.DatabaseStructure import DatabaseStructure
from Helpers.Change import Change
from Structures.QueryStructure import QueryStructure
from Structures.Relation import Relation, Attribute


def transform(query: Query, changes: list[Change], old_structure: list[Table], new_structure: list[Table]):
    old_structure = DatabaseStructure(old_structure)
    new_structure = DatabaseStructure(new_structure)
    if query.has_star_expression():
        transform_star_expression(old_structure, query)

    new_changes = create_changes_to_transform_ambiguous_columns(query, changes, old_structure, new_structure)
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

def create_changes_to_transform_ambiguous_columns(query: Query, changes: list[Change], old_structure: DatabaseStructure, new_structure: DatabaseStructure):
    query_structure = QueryStructure(query.get_tables(), query.get_columns())
    query_structure.resolve_columns(old_structure)
    query_structure.create_relations(old_structure)
    for change in changes:
        query_structure.change_relations(change, new_structure)

    new_changes = []
    for additional_change in query_structure.additional_changes:
        change_type, identifier, alias = additional_change
        if change_type == "add_column_alias":
            (table, column) = identifier
            new_changes.append(Change((Table(table), Column(column)), (Table(table), Column(column, alias))))

    return new_changes

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
