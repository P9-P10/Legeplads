from Structures.Column import Column
from Structures.Query import Query
from Structures.Table import Table
from Structures.DatabaseStructure import DatabaseStructure
from Helpers.Change import Change
from Structures.QueryStructure import QueryStructure
from Structures.Relation import Relation, Attribute
from Structures.Node import TableNode, ColumnNode


def transform(query: Query, changes: list[Change], old_tables: list[Table], new_tables: list[Table]):
    old_structure = DatabaseStructure(old_tables)
    new_structure = DatabaseStructure(new_tables)

    # Extract and transform subqueries separately
    subqueries = query.extract_subqueries()
    for subquery in subqueries:
        transform(subquery, changes, old_tables, new_tables)

    if query.has_star_expression():
        transform_star_expression(old_structure, query)

    new_changes = create_changes_to_transform_ambiguous_columns(query, changes, old_structure, new_structure)
    all_changes = changes + new_changes
    apply_each_change(query, all_changes)
    # Reinsert the transformed subqueries
    query.insert_subqueries(subqueries)


def transform_star_expression(old_structure: DatabaseStructure, query: Query):
    for table in query.get_tables():
        current_columns = query.get_columns()
        new_columns = old_structure.get_columns_in_table(table.name)
        for new_column in new_columns:
            # Check if a column with the same name is already in the query
            if new_column.name in [other_column.name for other_column in current_columns]:
                # If the table defines an alias use that, otherwise use the table name
                if table.alias:
                    new_column.add_alias(table.alias)
                else:
                    new_column.add_alias(table.name)

        query.add_to_select(new_columns)


def create_changes_to_transform_ambiguous_columns(query: Query, changes: list[Change], old_structure: DatabaseStructure, new_structure: DatabaseStructure):
    ast_alias_nodes = query.get_alias_nodes()
    ast_table_nodes = query.get_table_nodes()
    ast_column_nodes = query.get_column_nodes()

    table_nodes_with_alias = [TableNode(ast_node) for ast_node in ast_alias_nodes]
    table_nodes = [TableNode(ast_node) for ast_node in ast_table_nodes]

    names_of_tables_with_alias = [alias_node.get_name() for alias_node in table_nodes_with_alias]
    all_table_nodes = table_nodes_with_alias + \
                      [node for node in table_nodes if node.get_name() not in names_of_tables_with_alias]
    column_nodes = [ColumnNode(ast_node) for ast_node in ast_column_nodes]
    
    query_structure = QueryStructure(all_table_nodes, column_nodes, old_structure)
    query_structure.create_relations()
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
