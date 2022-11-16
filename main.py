from Applications.Database_intefaces.sqliteinterface import SqLiteInterface
from Graph.sql_lite_changes_parser import JsonChangesParser
from Graph.turtle_parser import TurtleParser
from Helpers.config_manager import ConfigManager
from Structures.Query import Query

config = ConfigManager("config.yml")
graphStorage = SqLiteInterface(config.get_config_value("changes_location"))
changes_string = graphStorage.run_query(Query("SELECT * FROM DatastoreGraphs"))
tables = graphStorage.run_query(Query("SELECT tables FROM DatastoreGraphs"))
changes = JsonChangesParser(changes_string)

for table in tables:
    databases = TurtleParser(table)