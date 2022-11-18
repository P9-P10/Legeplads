from Graph.changes_parser import ChangesParser
from Graph.graph_parser import GraphParser
from Structures.DataStore import DataStore
from Structures.Schema import Schema


class version_manager:
    class Change:
        def __init__(self, time=0, old=None, new=None, database_id=None):
            self.from_time = time
            self.old = old
            self.new = new
            self.database_id = database_id

        def __eq__(self, other):
            return self.from_time == other.from_time \
                   and self.old == other.old \
                   and self.new == other.new \
                   and self.database_id == other.database_id

        def __repr__(self):
            return "Time: " + str(self.from_time) + " Old: " + str(self.old) + " New: " + str(
                self.new) + " ID: " + self.database_id

    def __init__(self, database_parser: GraphParser, changes_parser: ChangesParser, tables, input_changes):
        def get_old_and_new_datastore(query_id) -> (DataStore, DataStore):

            out = []
            for key, table in versions.items():
                if table[1] == query_id:
                    out.append(table[0])

                    if len(out) == 2:
                        return out

        def get_changes():
            for change in input_changes:
                from_time = change[0]
                operations = change[1]
                if not operations == "[]":
                    change_id = change[2]
                    old, new = get_old_and_new_datastore(change_id)
                    parsed = changes_parser.get_changes(old, new, operations)
                    for current_change in parsed:
                        self.changes.append(
                            self.Change(from_time, current_change[0], current_change[1], database_id=change_id))

        def get_database_versions():
            for table in tables:
                from_time = table[0]
                graph = table[1]
                table_id = table[2]
                parsed_database = database_parser.get_structure(graph)
                if from_time in versions:
                    versions[from_time] = (parsed_database, table_id, ())
                else:
                    versions.update({from_time: (parsed_database, table_id, ())})

        self.changes: [version_manager.Change] = []
        versions: dict[str, []] = {}
        self.database_parser: GraphParser = database_parser
        get_database_versions()
        get_changes()

    def get_change_for_column(self, schema_name="main", table_name="", column_name="") -> Schema | None:
        for change in self.changes:
            if change.old.name == schema_name:
                schema = change.old
                for table in schema.tables:
                    if table.name == table_name:
                        for column in table.columns:
                            if column.name == column_name:
                                return change.new
        return None
