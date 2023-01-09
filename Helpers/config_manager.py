from os.path import exists
import yaml


class ConfigManager:
    config = {}

    def __init__(self, file_path):
        self.file_path = file_path
        self.error = ValueError("Please configure the config in: " + file_path)
        if self.config == {}:
            if exists(file_path):
                with open(file_path) as file:
                    self.config = yaml.safe_load(file)
                    for key, value in self.config.items():
                        if value == "":
                            raise self.error
            else:
                with open(file_path, "w") as file:
                    config = {"changes_location": "", "database_versions_location": "","database_connections":[]}
                    yaml.dump(config, file)
                    self.config = config

    def get_config(self):
        for key, value in self.config.items():
            if value == "":
                raise self.error
        return self.config

    def get_config_value(self, value):
        if self.config[value] == "":
            raise self.error
        return self.config[value]
