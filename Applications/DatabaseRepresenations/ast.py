from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column
from sqlglot import parse_one, exp

class AST:
    def __init__(self, ast):
        self.ast = ast

    def transform_ast(self, transformer):
        self.ast = self.ast.transform(transformer)

    def sql(self):
        return self.ast.sql()

    def replace_table(self, old_table: Table, new_table: Table):
        def transform(node):
            if isinstance(node, exp.Table) and node.name == str(old_table):
                return parse_one(str(new_table))
            return node

        self.transform_ast(transform)

    def create_alias_map(self):
        alias_map = {}
        for alias in self.ast.find_all(exp.Alias):
            self.add_alias_if_exists(alias, alias_map)
        return alias_map

    def add_alias_if_exists(self, alias, alias_map):
        if alias.find(exp.Table) is not None:
            table = alias.find(exp.Table).name
            table_alias = alias.find(exp.TableAlias).name
            alias_map[table] = table_alias

    def apply_missing_aliases(self, tables, alias_map):
        if not tables:
            return
        
        def transformer(node):
            if isinstance(node, exp.Column):
                if self.node_has_no_table(node):
                    return self.apply_alias_to_node(node, self.get_alias_for_column(tables, alias_map, node.name))
                elif node.table in [table.name for table in tables]:
                    return self.apply_alias_to_node(node, self.get_alias_for_table(node.table, alias_map))
            return node

        self.transform_ast(transformer)

    def node_has_no_table(self, node):
        return node.table == ""

    def apply_alias_to_node(self, node, alias):
        return node.replace(exp.Column(
            this=exp.Identifier(this=node.name),
            table=exp.Identifier(this=alias)))

    def create_needed_aliases(self):
        def transform(node):
            if isinstance(node, exp.Table):
                if not isinstance(node.parent, exp.Alias):
                    return self.create_alias_on_node(node)
            return node

        self.transform_ast(transform)

    def create_alias_on_node(self, node):
        return node.replace(exp.Alias(
            this=exp.Table(
                this=exp.Identifier(this=node.name, quoted=False)),
            alias=exp.TableAlias(
                this=exp.Identifier(this=node.name + "1"))
        ))

    def get_alias_for_table(self, table_name, table_map):
        return table_map[table_name]

    def get_alias_for_column(self, tables, aliases, column_name):
        column_table = self.get_table_for_column(tables, column_name)
        return aliases[column_table]

    def get_table_for_column(self, tables, column_name):
        for table in tables:
            if table.has_column(Column(column_name)):
                return table.name