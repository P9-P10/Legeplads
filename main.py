from Applications.Database_intefaces.sqliteInterfaceWIthChanges import SqLiteInterfaceWithChanges
from Applications.Database_intefaces.sqliteinterface import SqLiteInterface
from Graph.json_changes_parser import JsonChangesParser
from Graph.turtle_parser import TurtleParser
from Graph.version_manager import version_manager
from Helpers.config_manager import ConfigManager
from Structures.Query import Query

config = ConfigManager("config.yml")
graphStorage = SqLiteInterface(config.get_config_value("changes_location"))
changes_string = graphStorage.run_query(Query("SELECT id,operations,uri FROM DatastoreGraphs"))
tables = graphStorage.run_query(Query("SELECT id,graph,uri FROM DatastoreGraphs"))

vm = version_manager(TurtleParser(), JsonChangesParser(), tables, changes_string)
database_name = "http://www.test.com/SimpleDatabase"
sqlite_change = SqLiteInterfaceWithChanges("Databases/AdvancedDatabase.sqlite",
                                           vm.get_operations_for_version(2, database_name),
                                           vm.get_data_store_for_change(2, database_name))
print(vm)
