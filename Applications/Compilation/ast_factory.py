from sqlglot import exp

"""
This module contains methods for creating elements of an AST for a query.
"""

def create_identifier(name: str):
    return exp.Identifier(this=name)

def create_column(name, table=None):
    if table:
        return exp.Column(
            this=create_identifier(name),
            table=create_identifier(table)
        )
    else:
        return exp.Column(this=create_identifier(name))

def create_table(name: str):
    return exp.Table(this=create_identifier(name))

def create_simple_join(table_name: str, table_alias: str = None):
    if table_alias:
        return exp.Join(this=create_table_with_alias(table_name, table_alias))
    else:
        return exp.Join(this=create_table(table_name))

def create_join_with_condition(table_name: str, condition: exp.Expression, table_alias: str = None):
    if table_alias:
        return exp.Join(this=create_table_with_alias(table_name, table_alias), on=condition)
    else:
        return exp.Join(this=create_table(table_name), on=condition)

def create_from_with_table(table_name: str, table_alias: str = None):
    if table_alias:
        return exp.From(expressions=[create_table_with_alias(table_name, table_alias)])
    else:
        return exp.From(expressions=[create_table(table_name)])

def create_table_with_alias(table_name: str, table_alias: str):
    return exp.Alias(this=create_table(table_name), alias=exp.TableAlias(this=create_identifier(table_alias)))

def create_where_with_condition(condition: exp.Expression):
    return exp.Where(this=condition)

def create_star_selection():
    return [exp.Star()]