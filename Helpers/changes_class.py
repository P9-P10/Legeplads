from Helpers.deletion_rules import DeletionRule as dr


class Changes:
    def __init__(self, new_name: str = "", how_to_delete: dr = dr(), row_map=None):
        if row_map is None:
            self.old_to_new_column_map = {}
        else:
            self.old_to_new_column_map = row_map
        self.new_name = new_name
        self.should_rename = self.new_name != ""
        self.how_to_delete = how_to_delete
