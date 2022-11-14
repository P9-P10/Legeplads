from os.path import exists
import yaml


class ConfigManager:
    config = {}

    def __init__(self, file_path):
        self.file_path = file_path
        if self.config == {}:
            if exists(file_path):
                with open(file_path) as file:
                    self.config = yaml.safe_load(file)
            else:
                with open(file_path,"w") as file:
                    config = {"changes_location": "", "database_versions_location": ""}
                    yaml.dump(config, file)
                    self.config = config

    def get_config(self):
        return self.config

    def get_config_value(self,value):
        return self.config[value]


