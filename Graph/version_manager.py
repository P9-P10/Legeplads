from Graph.changes_parser import ChangesParser
from Graph.graph_parser import GraphParser
from Structures.DataStore import DataStore


class version_manager:
    def __init__(self, database_parser: GraphParser, changes_parser: ChangesParser, tables, changes):
        def get_old_and_new_datastore(query_id) -> (DataStore, DataStore):

            out = []
            for key, table in self.versions.items():
                if table[1] == query_id:
                    out.append(table[0])

                    if len(out) == 2:
                        return out

        def get_changes():
            for change in changes:
                from_time = change[0]
                graph = change[1]
                if not graph == "[]":
                    change_id = change[2]
                    old, new = get_old_and_new_datastore(change_id)
                    parsed = changes_parser.get_changes(old, new, graph)
                    old_value = self.versions[from_time]
                    self.versions.update({from_time: (old_value[0],old_value[1], parsed)})

        def get_database_versions():
            for table in tables:
                from_time = table[0]
                graph = table[1]
                table_id = table[2]
                parsed_database = database_parser.get_structure(graph)
                if from_time in self.versions:
                    self.versions[from_time] = (parsed_database, table_id,())
                else:
                    self.versions.update({from_time: (parsed_database, table_id,())})

        self.versions: dict[str, []] = {}
        self.database_parser: GraphParser = database_parser
        get_database_versions()
        get_changes()
