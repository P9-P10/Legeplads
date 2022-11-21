from sqlglot import exp

class Relation:
    def __init__(self, name: str, alias: str, index: int):
        self.name = name
        self.alias = alias
        self.index = index
    
    def __repr__(self):
        return f'Relation(Name: {self.name}, Alias: {self.alias}, Index: {self.index})'

    def change_alias(self, new_alias: str):
        self.alias = new_alias


class Attribute:
    def __init__(self, name, relation_index):
        self.name = name
        self.relation_index = relation_index

    def __repr__(self):
        return f'Attribute(Name: {self.name}, Relation_index: {self.relation_index})'

    def change_relation(self, new_index: int):
        self.relation_index = new_index


class Expression:
    """
    An Expression is some part of a query that contains attributes.
    The purpose of the class is to be able to manipulate the attributes that appear in elements of the query,
    without having to be concerned with the type of the element.
    """

    def __init__(self, expression: exp.Expression, attributes: list[Attribute]):
        self.expression = expression
        self.attributes = attributes

    def change_attributes(self, new_attributes: list[Attribute]):
        self.attributes = new_attributes

    def change_references_to_relations_in_attributes(self, indicies_to_replace: list[int], new_index: int):
        for attr in self.attributes:
            if attr.relation_index in indicies_to_replace:
                attr.change_relation(new_index)


class Join:
    def __init__(self, relation_index: int, expression: Expression):
        self.relation_index = relation_index
        self.expression = expression

    def change_relation(self, new_index: int):
        self.relation_index = new_index


# TODO: Change to use Expression instead of list of attributes and condition
class FromExpr:
    def __init__(self, relation_indicies: list[int], condition: Expression):
        self.relation_indicies = relation_indicies
        self.condition = condition
    
    def change_references_to_relations_in_attributes(self, indicies_to_replace: list[int], new_index: int):
        self.condition.change_references_to_relations_in_attributes(indicies_to_replace, new_index)