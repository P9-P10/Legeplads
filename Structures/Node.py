from sqlglot import exp

class EntityNode:
    def __init__(self, query_node, name: str, alias: str = None):
        self.query_node = query_node
        self.name = name
        self.alias = alias

    def __repr__(self):
        return f'Node(Name: {self.name} Alias: {self.alias})'

    def get_name(self):
        return self.name

    def has_alias(self):
        return True if self.alias else False

    def get_alias(self):
        if not self.has_alias():
            raise AttributeError(f'Alias for node with name: {self.name} is not defined')
        return self.alias

    def get_query_node(self):
        return self.query_node

    def create_new_query_node(self):
        pass

class ColumnNode(EntityNode):
    def __init__(self, query_node: exp.Column):
        if not isinstance(query_node, exp.Column):
            raise TypeError(f'ColumnNode expects a parameter of type sqlglot.exp.Column but got {type(query_node)}')
        super().__init__(query_node, query_node.name, query_node.table)

    def create_new_query_node(self):
        return create_column(self.name, self.alias)

class TableNode(EntityNode):
    def __init__(self, query_node: exp.Alias | exp.Table):
        if isinstance(query_node, exp.Table):
            super().__init__(query_node, query_node.name)
        elif isinstance(query_node, exp.Alias):
            super().__init__(query_node, query_node.this.name, query_node.alias)
        else:
            raise TypeError(f'TableNode expects a parameter of type sqlglot.exp.Table or sqlglot.exp.Alias but got {type(query_node)}')

    def create_new_query_node(self):
        if self.has_alias():
            return create_table(self.name, self.alias)
        else:
            return create_table(self.name)


def create_column(name, table=None):
    if table:
        return exp.Column(
            this=create_identifier(name),
            table=create_identifier(table)
        )
    else:
        return exp.Column(this=create_identifier(name))

def create_identifier(name: str):
    return exp.Identifier(this=name)


def create_table(name, alias=None):
    if alias:
        return exp.Alias(this=create_table(name), alias=exp.TableAlias(this=create_identifier(alias)))
    else:
        return exp.Table(this=create_identifier(name))
