from collections import defaultdict
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Structure import Structure
from Structures.Table import Table
from Structures.Relation import Relation, Attribute
from Helpers.Change import Change
from Structures.Node import TableNode, ColumnNode

class QueryStructure:
    def __init__(self, table_nodes: list[TableNode], column_nodes: list[ColumnNode], db_structure: DatabaseStructure):
        self.table_nodes = table_nodes
        self.column_nodes = column_nodes
        self.db_structure = db_structure
        self.table_to_alias_map = {}
        self.alias_to_table_map = {}
        self.alias_count = 1
        self.additional_changes = []
        self.relations = []
        

    def get_columns(self):
        return self.columns


    def get_column(self, column_name: str):
        for column in self.columns:
            if column.name == column_name:
                return column


    def create_alias_maps(self):
        # Populate dictionary to map aliases to table names
        for table_node in self.table_nodes:
            if table_node.has_alias():
                self.alias_to_table_map[table_node.get_alias()] = table_node.get_name()
                self.table_to_alias_map[table_node.get_name()] = table_node.get_alias()


    def create_relations(self):
        self.create_alias_maps()
        table_to_columns_map = self.map_tables_to_columns()

        for table_node in self.table_nodes:
            # Aggregate functions show up as tables, but they have no name
            # Relations should not be create for aggregates
            if table_node.get_name():
                database_table = self.db_structure.get_table(table_node.get_name())
                attributes = []
                for column_node in table_to_columns_map[table_node.get_name()]:
                    attributes.append(Attribute(column_node, database_table.get_column(column_node.get_name()), column_node.has_alias()))
                alias = "" if not table_node.has_alias() else table_node.get_alias()
                self.relations.append(Relation(table_node, database_table, attributes, alias))


    def map_tables_to_columns(self):
        # Tables have multiple columns, so the values of the dict should be lists
        # The defaultdict ensures that all values are the empty list by default
        # This removes the need to handle assigning a singleton list on adding the first element for a key 
        table_to_columns_map = defaultdict(list)
        for column_node in self.column_nodes:
            if column_node.has_alias():
                alias = column_node.get_alias()
                # If it has an alias, it should either be in the alias map, or it should be a table name
                if alias in self.alias_to_table_map.keys():
                    table_name = self.alias_to_table_map[alias]
                else:
                    table_name = alias
                table_to_columns_map[table_name].append(column_node)
            else:
                # Do a brute force search
                for table in self.db_structure.get_all_tables():
                    for column in table.columns:
                        if column.name == column_node.get_name():
                            table_to_columns_map[table.name].append(column_node)
        return table_to_columns_map


    def get_table_from_structure(self, table: Table, db_structure: DatabaseStructure):
        return db_structure.get_table(table.name)


    def change_relations(self, change: Change, new_structure: DatabaseStructure):
        for relation in self.relations:
            if self.change_affects_relation(change, relation):
                # Check if the change changes the table of the relation
                table_changed = self.table_changed(change, relation)
                # Change the relation to point to the table in the new structure
                relation.table = self.get_table_from_structure(change.get_new_table(), new_structure)
                self.change_attributes(change, new_structure, relation)
                # Relation is now changed, and that may have made it, or some of its attributes, ambiguous
                # That is only the case if the same table is refered to several times, which in turn only occurs if the table has changed
                if table_changed:
                    self.resolve_ambiguos_tables(relation)


    def change_affects_relation(self, change: Change, relation: Relation):
        return relation.table.name == change.get_old_table().name


    def table_changed(self, change: Change, relation: Relation):
        return not change.get_new_table().name == relation.table.name


    def change_attributes(self, change: Change, new_structure: DatabaseStructure, relation: Relation):
        for attribute in relation.attributes:
            # Change column reference to columns in the new structure
            if attribute.column.name == change.get_old_column().name:
                # If the column has changed, change the reference to the new column
                column_name = change.get_new_column().name
            else:
                # otherwise change it to the column with the same name
                column_name = change.get_old_column().name
            for db_col in new_structure.get_table(change.get_new_table().name).columns:
                if db_col.name == column_name:
                    attribute.column = db_col


    def resolve_ambiguos_tables(self, relation: Relation):
        for other_relation in self.relations:
            # Do not compare with the same relation
            if other_relation == relation:
                continue
            if other_relation.table.name == relation.table.name:
                # In this case, all attributes from both relations have to use an alias, and the alias can not be the table name
                self.ensure_alias_on_all_attributes(other_relation)
                self.ensure_alias_on_all_attributes(relation)


    def ensure_alias_on_all_attributes(self, relation: Relation):
        # Create an alias for the relation if it does not already have one
        if relation.alias == "":
            # Create a simple alias by appending a number to the table name
            relation.alias = relation.table.name + str(self.alias_count)
            # Increment the number to ensure no relations have the same alias, even if they have the same table name
            self.alias_count += 1
            # Add the change to additional changes (so it can be used to actually change the query)
            self.additional_changes.append(("add_table_alias", relation.table.name, relation.alias))
        
        # Ensure that all attributes in the relation are configured to use the alias
        # Add a change to additional changes if an attribute did not previously use an alias
        for attr in relation.attributes:
            if not attr.use_alias:
                attr.use_alias = True
                self.additional_changes.append(("add_column_alias", (relation.table.name, attr.column.name), relation.alias))
