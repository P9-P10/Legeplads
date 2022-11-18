from Applications.Database_intefaces.sqliteinterface import SqLiteInterface
from Graph.json_changes_parser import JsonChangesParser
from Graph.turtle_parser import TurtleParser
from Graph.version_manager import version_manager
from Helpers.config_manager import ConfigManager
from Structures.Query import Query

config = ConfigManager("config.yml")
graphStorage = SqLiteInterface(config.get_config_value("changes_location"))
changes_string = graphStorage.run_query(Query("SELECT from_date,operations,uri FROM DatastoreGraphs"))
tables = graphStorage.run_query(Query("SELECT from_date,graph,uri FROM DatastoreGraphs"))


vm = version_manager(TurtleParser(), JsonChangesParser(), tables, changes_string)

print(vm)
