from Structures.DatabaseStructure import DatabaseStructure
from Structures.Structure import Structure
from Structures.Table import Table
from Structures.Column import Column
from Structures.Relation import Relation, Attribute
from Helpers.Change import Change

class QueryStructure(Structure):
    def __init__(self, tables: list[Table], columns: list[Column]):
        self.tables = self.copy_list(tables)
        self.columns = self.copy_list(columns)
        self.alias_map = {}
        self.alias_count = 1

    def __eq__(self, other):
        if not isinstance(other, QueryStructure):
            return False
        
        return set(self.tables) == set(other.tables) and set(self.columns) == set(other.columns)

    def copy_list(self, list):
        return [elem.copy() for elem in list]

    def copy(self):
        return QueryStructure(self.tables, self.columns)

    def get_columns(self):
        return self.columns

    def get_columns_with_name(self, name: str) -> list[Column]:
        return [column for column in self.columns if column.name == name]

    def resolve_columns(self, db_structure: DatabaseStructure):
        # Populate dictionary to map aliases to table names
        for table in self.tables:
            if table.alias:
                self.alias_map[table.alias] = table.name
        
        def fun(column: Column):
            if column.alias:
                # If it has an alias, it should either be in the alias map, or it should be a table name
                if column.alias in self.alias_map.keys():
                    column.set_table_name(self.alias_map[column.alias])
                else:
                    column.set_table_name(column.alias)
            else:
                column.set_table_name(db_structure.get_table_for_column(column).name)

        self.columns = [column.transform(fun) for column in self.columns]

    def create_relations(self, old_structure):
        relations = []
        for query_table in self.tables:
            # Aggregate functions may show up as tables if they have an alias, but they have no name
            if query_table.name:
                database_table = old_structure.get_table(query_table.name)
                database_columns = database_table.columns
                query_columns = [column for column in self.columns if column.table_name == database_table.name]
                attributes = []
                for query_column in query_columns:
                    for db_col in database_columns:
                        if db_col.name == query_column.name:
                            # Set use alias flag to true if query_column defines an alias
                            use_alias = query_column.alias is not None
                            attributes.append(Attribute(db_col, use_alias))
                alias = "" if not query_table.alias else query_table.alias
                relations.append(Relation(database_table, attributes, alias))
        
        self.relations = relations

    def change_relations(self, change: Change, new_structure: DatabaseStructure):
        for relation in self.relations:
            table_changed = False
            if relation.table.name == change.get_old_table().name:
                if not change.get_new_table().name == relation.table.name:
                    # if the table has changed, change the reference to the table in the new structure
                    relation.table = new_structure.get_table(change.get_new_table().name)
                    table_changed = True
                for attribute in relation.attributes:
                    if attribute.column.name == change.get_old_column().name:
                        for db_col in new_structure.get_table(change.get_new_table().name).columns:
                            if db_col.name == change.get_new_column().name:
                                attribute.column = db_col
                    else:
                        for db_col in new_structure.get_table(change.get_new_table().name).columns:
                            if db_col.name == change.get_old_column().name:
                                attribute.column = db_col
            # Relation is now changed, and that may have made it, or some of its attributes ambiguous
            # That is only the case if the same table is refered to several times, which in turn only occurs if the table has changed
            if table_changed:
                for other_relation in self.relations:
                    # Do not compare with self
                    if other_relation == relation:
                        continue
                    if other_relation.table == relation.table:
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
        
        # Ensure that all attributes in the relation are configured to use the alias
        for attr in relation.attributes:
            attr.use_alias = True
