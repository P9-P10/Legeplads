from os.path import exists


class FileReader:
    def __init__(self, location):
        self.location = location
        if not exists(location):
            raise FileNotFoundError("The file: " + location + " does not exist.")

    def get_content(self)->str:
        with open(self.location) as f:
            return f.read()
