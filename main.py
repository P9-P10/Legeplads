from Applications.Database_intefaces.sqliteInterfaceWIthChanges import SqLiteInterfaceWithChanges
from Applications.Database_intefaces.sqliteinterface import SqLiteInterface
from Graph.json_changes_parser import JsonChangesParser
from Graph.operations_maker import OperationsMaker
from Graph.turtle_parser import TurtleParser
from Graph.versionmanager import VersionManager
from Helpers.config_manager import ConfigManager
from Structures.Query import Query


def database_to_uri(database: str):
    return "http://www.test.com/" + database.split(".")[0]


config = ConfigManager("config.yml")
graphStorage = SqLiteInterface(config.get_config_value("changes_location"))
changes_string = graphStorage.run_query(Query("SELECT id,operations,uri FROM DatastoreGraphs"))
tables = graphStorage.run_query(Query("SELECT id,graph,uri FROM DatastoreGraphs"))

vm = VersionManager(TurtleParser(), JsonChangesParser(), tables, changes_string)
operations_maker = OperationsMaker(vm)
database_name = "http://www.test.com/SimpleDatabase"

databases = config.get_config_value("database_connections")
db_instances = []
for database in databases:
    uri = database_to_uri(database)
    version = len(changes_string)
    operations = operations_maker.get_operations_for_version(version, uri)
    old_dataStore, new_dataStore = vm.get_data_stores_for_change(version, uri)
    if not old_dataStore:
        # It does not appear that this case will work
        # If the value of old_dataStore is None, it is passed to sqliteInterfaceWithChanges
        # which expectes a list of tables
        db_change = SqLiteInterfaceWithChanges("Databases/" + database, operations,
                                               old_dataStore,
                                               new_dataStore)
    else:
        db_change = SqLiteInterfaceWithChanges("Databases/" + database,
                                               operations,
                                               old_dataStore.schemas[0].tables,
                                               new_dataStore.schemas[0].tables)
    db_instances.append(db_change)

while True:
    query = input("Please enter a query you want to run: ")
    for db in db_instances:
        print("Query " + query + " Was run on: " + db.path_to_database)
        q = Query(query)
        result = db.run_query(q)
        print(result)
