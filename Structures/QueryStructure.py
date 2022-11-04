from Structures.DatabaseStructure import DatabaseStructure
from Structures.Structure import Structure
from Structures.Table import Table
from Structures.Column import Column
from Structures.Relation import Relation, Attribute
from Helpers.Change import Change

class QueryStructure(Structure):
    def __init__(self, tables: list[Table], columns: list[Column]):
        self.tables = tables
        self.columns = columns
        self.table_alias_map = {}
        self.alias_count = 1
        self.additional_changes = []

    def __eq__(self, other):
        if not isinstance(other, QueryStructure):
            return False
        
        return set(self.tables) == set(other.tables) and set(self.columns) == set(other.columns)

    def copy(self):
        return QueryStructure(self.tables, self.columns)

    def get_columns(self):
        return self.columns

    def get_column(self, column_name: str):
        for column in self.columns:
            if column.name == column_name:
                return column

    def resolve_columns(self, db_structure: DatabaseStructure):
        # Populate dictionary to map aliases to table names
        for table in self.tables:
            if table.alias:
                self.table_alias_map[table.alias] = table.name

        for column in self.columns:
            if column.alias:
                # If it has an alias, it should either be in the alias map, or it should be a table name
                if column.alias in self.table_alias_map.keys():
                    column.set_table_name(self.table_alias_map[column.alias])
                else:
                    column.set_table_name(column.alias)
            else:
                column.set_table_name(db_structure.get_table_for_column(column).name)

    def create_relations(self, old_structure: DatabaseStructure):
        relations = []
        for query_table in self.tables:
            # Aggregate functions may show up as tables if they have an alias, but they have no name
            if self.has_name(query_table):
                database_table = self.get_table_from_structure(query_table, old_structure)
                attributes = self.create_attributes_for_relation(database_table)
                alias = "" if not query_table.alias else query_table.alias
                relations.append(Relation(database_table, attributes, alias))
        
        self.relations = relations

    def has_name(self, table: Table):
        # Aggregate functions may show up as tables if they have an alias, but they have no name
        return True if table.name else False

    def get_table_from_structure(self, table: Table, structure: DatabaseStructure):
        return structure.get_table(table.name)

    def create_attributes_for_relation(self, database_table: Table):
        attributes = []
        # Requires finding the column in the table, and finding the alias from the list of columns in the query
        for column_in_query in self.get_columns_in_table(database_table):
            for db_col in database_table.columns:
                if db_col.name == column_in_query.name:
                    # Set use alias flag to true if query_column defines an alias
                    use_alias = column_in_query.alias is not None
                    attributes.append(Attribute(db_col, use_alias))
                    
        return attributes

    def get_columns_in_table(self, table: Table):
        return [column for column in self.columns if column.table_name == table.name]

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
