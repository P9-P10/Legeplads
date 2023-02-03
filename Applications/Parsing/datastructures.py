from .primitives import *
import Applications.Compilation.ast_factory as AST

class RangeTable:
    """
    The range table maintains an index of the relations present in the query.
    Each relation has a unique index so they can be referred to unambiguously.
    The index will continue to refer to the same relation, 
    even if the name or alias should change.
    """
    def __init__(self):
        self.relations = []
        self.relation_names = []
    
    def append(self, name: str, alias: str) -> int:
        """
        Adds a relation to the query.
        Returns the index of the added relation.
        """
        relation = Relation(name, alias, len(self.relations))
        self.relations.append(relation)
        self.relation_names.append(name)

        self.ensure_table_is_not_ambiguous(name)

        # Return the index of the added item
        return relation.index

    def ensure_table_is_not_ambiguous(self, table_name: str) -> None:
        """
        If the given table name is ambiguous, aliases are created for all instances.
        """
        # The automatic creation of aliases could be a setting, so that it is possible for
        # the caller to determine if they want aliases to be generated.
        indicies_of_relations_with_name = self.index_of_entries_with_name(table_name)
        if len(indicies_of_relations_with_name) > 1:
            for occurence, index in enumerate(indicies_of_relations_with_name):
                relation = self.get_relation_with_index(index)
                if relation.alias == "" or relation.alias == relation.name:
                    relation.change_alias(relation.name + str(occurence + 1))

    def contains(self, table_name) -> bool:
        return table_name in self.relation_names

    def index_of_entries_with_name(self, table_name) -> list[int]:
        """Returns a list containing the indicies of all relations with a matching name."""
        return [relation.index for relation in self.relations if relation.name == table_name]

    def index_of_matching_relation(self, name: str, alias: str):
        return self.get_matching_relation(name, alias).index
    
    def get_matching_relation(self, name: str, alias: str) -> Relation:
        """
        Returns the relation with matching name and alias.
        Given a non-empty alias there should be at most one match, as multiple occurences of the same alias is invalid.
        """
        for relation in self.relations:
            if relation.name == name and relation.alias == alias:
                return relation
                # TODO raise exception if there is no match

    def get_relation_for_attribute(self, attribute: Attribute) -> Relation:
        return self.relations[attribute.relation_index]

    def get_relation_with_alias(self, alias: str):
        """
        Returns the relation with the given alias.
        There should be at most one match, as multiple occurences of the same alias is invalid.
        """
        for relation in self.relations:
            if relation.alias == alias:
                return relation
        # TODO raise exception if there is no match

    def get_relation_with_index(self, index: int):
        return self.relations[index]


class Selection:
    """
    The selection maintains a list of the Expressions in the select statement.
    An expression in the selection will contain one or more attributes, each 
    of which has a reference to the relation they are selected from.
    """
    def __init__(self, range_table: RangeTable, selection: list[Expression], select_star: bool):
        self.range_table = range_table
        self.selection_list = selection
        self.select_star = select_star
        self.initial_selection = selection

    def change_references_to_relations_in_attributes(self, old_indicies: list[int], new_index: int):
        """Change all matching references to old_index in the attributes in the selection to refer to new_index"""
        for expr in self.selection_list:
            expr.change_references_to_relations_in_attributes(old_indicies, new_index)

    # manipulation
    def get_unused_relations(self):
        """
        Returns a list of all relations in the range table that are not referenced by any 
        attributes in the selection.
        """
        if self.select_star:
            return []

        # Using a set to maintain indicies of referenced relations
        # as duplicates are not needed, and better performance for membership testing
        indicies_of_used_relations = set()
        # Create set used relations
        for expr in self.selection_list:
            for attribute in expr.attributes:
                indicies_of_used_relations.add(attribute.relation_index)
        
        # Construct and return list of all relations not present in the set
        return [relation for relation in self.range_table.relations if relation.index not in indicies_of_used_relations]


class JoinTree:
    """
    The join tree maintains the order of expressions in the 'FROM' clause of a query.
    These expressions can simply be the name of a table or they can be joins.
    Each of the expressions can have a condition which corresponds to the 'WHERE' clause 
    of a query or to the 'ON' clause of a join.
    """
    def __init__(self, range_table: RangeTable, from_indicies: list[int], where_expr: Expression, joins: list[Join]):
        self.range_table = range_table
        self.from_indicies = from_indicies
        self.where_expr = where_expr
        self.joins = joins

    def add_relation_without_condition(self, relation_index):
        """
        Adds a relation to the query.
        The relation is added to the 'FROM' clause if this is empty.
        Otherwise it is added as an inner join.
        """
        if self.is_from_empty():
            self.from_indicies = [relation_index]
        else: 
            relation = self.range_table.get_relation_with_index(relation_index)
            self.joins.append(Join(relation, Expression(None, [])))
            
    def is_from_empty(self) -> bool:
        return len(self.from_indicies) == 0

    # manipulation
    def remove_relation(self, relation: Relation):
        """
        Removes the occurences of a relation from the 'FROM' clause and from joins.
        """
        # Remove from 'FROM' clause
        self.from_indicies = [index for index in self.from_indicies if not index == relation.index]

        # Remove from joins
        self.joins = [join for join in self.joins if not join.relation.index == relation.index]

        self.ensure_from_is_not_empty()
    
    def ensure_from_is_not_empty(self):
        """
        The removal of relations from the joins tree can result in the 'FROM' clause being empty.
        In this case the first join should be moved to the 'FROM' clause.
        """
        if len(self.from_indicies) == 0 and len(self.joins) > 0:
            first_join = self.joins.pop(0)
            self.from_indicies = [first_join.relation.index]
            self.where_expr.attributes = first_join.expression.attributes
            self.where_expr.ast = first_join.expression.ast
                
    # manipulation
    def change_references_to_relations_in_attributes(self, indicies_to_replace: list[int], new_index: int):
        for join in self.joins:
            join.expression.change_references_to_relations_in_attributes(indicies_to_replace, new_index)

    # manipulation
    def move_condition(self, indicies_to_replace: list[int], new_index: int):

        for join in self.joins:
            if join.relation == self.range_table.get_relation_with_index(new_index):
                new_join = join
                break

        for join in self.joins:
            if join.relation.index in indicies_to_replace:
                new_join.expression.change_attributes(join.expression.attributes)
                new_join.expression.ast = join.expression.ast

    def relations_used_in_conditions(self):
        """Returns a set containing the indicies of relations used in joins"""
        indicies = []
        for join in self.joins:
            for attribute in join.expression.attributes:
                indicies.append(attribute.relation_index)

        return set(indicies)


# TODO: Create [result relation](https://www.postgresql.org/docs/current/querytree.html) 
# This is not used for select queries
# For Insert, Update, and Delete commands the result relation is the relation where the changes will take effect