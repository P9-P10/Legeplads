from Applications.DatabaseRepresenations.Column import Column
from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Helpers.Change import Change


def transform(query: Query, changes: list[Change], old_structure: list[Table], new_structure: list[Table]):
    tables = query.tables_in_query()
    test_list = set(query.columns_in_query())
    columns = [Column(name, alias) for (name, alias) in test_list]
    old_query_structure = column_table_match(columns, tables, old_structure)
    new_query_structure = get_new_query_structure(old_query_structure, changes)

    # apply_structure_changes(query, old_structure, new_structure, alias_map)
    apply_each_change(query, changes, new_query_structure)


def get_new_query_structure(old_query_structure, changes: list[Change]):
    new_query_structure = {}
    for table in old_query_structure:
        changed = False
        for change in changes:
            if change.get_old_table().name == table.name:
                if change.get_new_table().name == table.name:
                    update_table_in_structure(new_query_structure, table.name, change.get_new_column())
                    changed = True
                else:
                    update_table_in_structure(new_query_structure, change.get_new_table().name, change.get_new_column())
                    changed = True


    return new_query_structure


def update_table_in_structure(query_structure: dict[Table], table_name, column):
    column_list = []

    for table in query_structure.values():
        column_list.extend(table.columns)
    should_have_alias = column in column_list
    # TODO: Ensure both columns with same name have alias
    if table_name in query_structure:
        temp_table = query_structure[table_name]

        temp_columns = temp_table.columns
        if should_have_alias:
            alias = temp_table.get_alias()
            if not alias:
                alias = generate_alias(table_name)
                temp_table.set_alias(alias)
            column.set_alias(alias)
        temp_columns.append(column)

        temp_table.columns = temp_columns
        query_structure[table_name] = temp_table
    else:
        query_structure[table_name] = Table(table_name, [column])


def generate_alias(table_name):
    return table_name + "1"


def column_table_match(columns, tables, old_structure: list[Table]):
    output = []
    for table_name in tables:
        output_columns = []

        temp_table = get_table_from_structure(old_structure, table_name)
        if temp_table:
            for column in columns:
                if temp_table.has_column_with_alias(column,temp_table.name):
                    output_columns.append(column)
        if output_columns:
            output_table = Table(table_name, output_columns)
            output.append(output_table)

    return output


def get_table_from_structure(old_structure: list[Table], table_name):
    for structure in old_structure:
        if structure.name == table_name:
            return structure


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


def apply_each_change(query, changes, new_query_structure):
    for change in changes:
        if change.get_new_table().name in new_query_structure:
            new_table = new_query_structure[change.get_new_table().name]
            if new_table.has_column(change.get_new_column()):
                new_column = new_table.get_column(change.get_new_column().name)
            else:
                new_column = change.get_new_column()

        else:
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
