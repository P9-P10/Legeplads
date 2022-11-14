from Applications.Database_intefaces.sqliteinterface import SqLiteInterface
from Graph.changesparser import ChangesParser
from Helpers.config_manager import ConfigManager
from Structures.DatabaseStructure import DatabaseStructure


class SQLChangesParser(ChangesParser):
    def __init__(self, changes: str, connection_string: str):
        super().__init__(changes)
        self.connection_string = connection_string
        cf = ConfigManager("ProgramConfig")
        self.sqlite = SqLiteInterface(cf.get_config_value("path_to_sql"))

    def get_changes(self, database_structure: DatabaseStructure):
        pass


