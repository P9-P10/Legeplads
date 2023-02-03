from Graph.changes_parser import ChangesParser
from Graph.graph_parser import GraphParser
from Structures.DataStore import DataStore
from Structures.Schema import Schema


class VersionManager:
    class Change:
        def __init__(self, version=0, old_schema: Schema = None, new_schema: Schema = None, database_id=None):
            self.version = version
            self.old = old_schema
            self.new = new_schema
            self.database_id = database_id

        def __eq__(self, other):
            return self.version == other.version \
                and self.old == other.old \
                and self.new == other.new \
                and self.database_id == other.database_id

        def __repr__(self):
            return "Version: " + str(self.version) + " Old: " + str(self.old) + " New: " + \
                str(self.new) + " ID: " + self.database_id

    def __init__(self, database_parser: GraphParser, changes_parser: ChangesParser, tables, input_changes):
        def get_changes():
            for change in input_changes:
                from_time = change[0]
                operations = change[1]
                if not operations == "[]":
                    change_id = change[2]
                    old, new = self.get_old_and_new_datastore(change_id)
                    parsed = changes_parser.get_changes(old, new, operations)
                    for current_change in parsed:
                        self.changes.append(
                            self.Change(from_time, current_change[0], current_change[1], database_id=change_id))

        def get_database_versions():
            for table in tables:
                version = table[0]
                graph = table[1]
                table_id = table[2]
                parsed_database = database_parser.get_structure(graph)
                if len(self.versions) > version:
                    self.versions[version] = (parsed_database, table_id)
                else:
                    self.versions.append((parsed_database, table_id))

        self.changes: [VersionManager.Change] = []
        self.versions = []
        self.database_parser: GraphParser = database_parser
        get_database_versions()
        get_changes()

    def get_old_and_new_datastore(self, database_id, version_nr=None) -> (DataStore, DataStore):
        out = []
        if not version_nr:
            version_nr = 0
        else:
            version_nr = version_nr - 2
        for i in range(version_nr, len(self.versions)):
            current_database_id = self.versions[i][1]
            content = self.versions[i][0]

            if current_database_id == database_id:
                out.append(content)
            if len(out) == 2:
                return out[1], out[0]
        return None, None

    def get_change_for_column(self, table_name, column_name, version, schema_name="main") -> Schema | None:
        for change in self.changes:
            if change.version == version and change.old.name == schema_name:
                schema = change.old
                for table in schema.tables:
                    if table.name == table_name:
                        for column in table.columns:
                            if column.name == column_name:
                                return change.new
        return None

    def get_data_stores_for_change(self, version, database_id) -> (DataStore, DataStore):
        return self.get_old_and_new_datastore(database_id, version)
