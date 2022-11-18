import pathlib


class DBConfig:
    def __init__(self, name, path = str(pathlib.Path(__file__).parent.parent.parent / 'Databases') + '\\', extension = '.sqlite'):
        self.path = path
        self.extension = extension
        self.name = name

    def get_path_to_database(self):
        return self.path + self.name + self.extension