from Graph.versionmanager import VersionManager
from Structures.Changes import MoveColumn, RenameColumn


class OperationsMaker:
    def __init__(self, version_manager: VersionManager):
        self.version_manager = version_manager

    def get_operations_for_version(self, version, database_name):
        output = []
        for change in self.version_manager.changes:
            if change.version == version and change.database_id == database_name:
                output.extend(self.get_operations_for_change(change))
        return output

    def get_operations_for_change(self, change: VersionManager.Change):
        operations = []
        old_column = change.old.tables[0].columns[0]
        new_colum = change.new.tables[0].columns[0]
        old_table = change.old.tables[0]
        new_table = change.new.tables[0]

        if old_column.name == new_colum.name:
            operations.append(MoveColumn(old_column.name, old_table.name, new_table.name))
        else:
            operations.append(RenameColumn(old_column, new_colum, old_table))
            if new_table.name != old_table.name:
                operations.append(MoveColumn(new_colum, old_table.name, new_table.name))

        return operations
