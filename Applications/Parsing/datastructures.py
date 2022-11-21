from .primitives import *
import Applications.Compilation.ast_factory as AST

class RangeTable:
    def __init__(self):
        self.relations = []
        self.relation_names = []
    
    def append(self, name: str, alias: str) -> int:
        relation = Relation(name, alias, len(self.relations))
        self.relations.append(relation)
        self.relation_names.append(name)
        # Return the index of the added item
        return relation.index

    def contains(self, table_name) -> bool:
        return table_name in self.relation_names

    def index_of_entries_with_name(self, table_name) -> list[int]:
        return [relation.index for relation in self.relations if relation.name == table_name]

    def index_of_matching_relation(self, name: str, alias: str):
        return self.get_matching_relation(name, alias).index
    
    def get_matching_relation(self, name: str, alias: str) -> Relation:
        for relation in self.relations:
            if relation.name == name and relation.alias == alias:
                return relation
                # TODO raise exception if there is no match

    def get_relation_for_attribute(self, attribute: Attribute) -> Relation:
        return self.relations[attribute.relation_index]

    def get_relation_with_alias(self, alias: str):
        for relation in self.relations:
            if relation.alias == alias or relation.name == alias:
                return relation
        # TODO raise exception if there is no match

    def get_relation_with_index(self, index: int):
        return self.relations[index]


class Selection:
    def __init__(self, range_table: RangeTable, selection: list[Expression], select_star: bool):
        self.range_table = range_table
        self.selection_list = selection
        self.select_star = select_star
        self.initial_selection = selection


    def change_references_to_relations_in_attributes(self, old_indicies: list[int], new_index: int):
        for expr in self.selection_list:
            expr.change_references_to_relations_in_attributes(old_indicies, new_index)


    # manipulation
    def get_unused_relations(self):
        if self.select_star:
            return []

        unused_relations = []
        for relation in self.range_table.relations:
            used = False
            for expr in self.selection_list:
                for attribute in expr.attributes:
                    if attribute.relation_index == relation.index:
                        used = True
            if not used:
                unused_relations.append(relation)

        return unused_relations


class JoinTree:
    def __init__(self, range_table: RangeTable, joins: list[Join]):
        self.range_table = range_table
        self.joins = joins

    # manipulation
    def add_join_without_condition(self, relation_index):
        relation = self.range_table.get_relation_with_index(relation_index)
        self.joins.append(Join(relation.index, Expression(None, [])))


    # manipulation
    def remove_relations_with_name(self, relation_name: str):
        self.joins = [join for join in self.joins if not self.range_table.get_relation_with_index(join.relation_index).name == relation_name]

    def remove_relation(self, relation: Relation):
        self.joins = [join for join in self.joins if not join.relation_index == relation.index]

    
    # manipulation
    def change_references_to_relations_in_attributes(self, indicies_to_replace: list[int], new_index: int):
        for join in self.joins:
            join.expression.change_references_to_relations_in_attributes(indicies_to_replace, new_index)

    # manipulation
    def move_condition(self, indicies_to_replace: list[int], new_index: int):
        for join in self.joins:
            if join.relation_index == new_index:
                new_join = join
                break

        for join in self.joins:
            if join.relation_index in indicies_to_replace:
                new_join.expression.change_attributes(join.expression.attributes)
                new_join.expression.ast = join.expression.ast

    def relations_used_in_conditions(self):
        indicies = []
        for join in self.joins:
            for attribute in join.expression.attributes:
                indicies.append(attribute.relation_index)

        return set(indicies)