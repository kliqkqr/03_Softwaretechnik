import pathlib
import yaml
import os
from shutil import copyfile # used for cloning the default config

from Config import Filter, Formen, Formengroesse, Rastergroesse, Stringordnung, Wechselzeitdauer


# Implemented for the YAML standard
class ConfigFile:

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, 'DefaultConfig\DefaultConfig.yml')

    def __init__(self, path=None, auto_create=True):
        # Prepare Path
        if path is None:
            self.path = pathlib.Path().resolve() / 'ConfigFile.yml'
        else:
            self.path = path
        config_file = pathlib.Path(self.path)

        # Add the setting objects
        self.settings = [Filter.Filter(), Formen.Formen(), Formengroesse.Formengroesse(), Rastergroesse.Rastergroesse(),
                         Stringordnung.Stringordnung(), Wechselzeitdauer.Wechselzeitdauer()]

        # Check the Path
        if not config_file.exists():
            # Create a default config, if the file does not exist
            if auto_create:
                copyfile(self.DEFAULT_CONFIG_PATH, self.path)
            else:
                raise FileNotFoundError("The provided path does not lead to an existing file!")


    def loadSettings(self):
        # Check if the file exists
        config_file = pathlib.Path(self.path)
        if not config_file.exists():
            raise FileNotFoundError("The provided path does not lead to an existing file!")

        with open(self.path, "r") as ymlfile:
            config = yaml.safe_load(ymlfile)

        # Iterate over the sections (only two)
        for section in config:
            if section == "Settings":
                # Iterate over the fields and check for available setting objects
                for field in config[section]:
                    value = config[section][field]
                    for setting in self.settings:
                        if setting.matches(field) and setting.testValue(config):
                            #setting.loadYML(value)
                            break

            elif section == "Database":
                # TODO
                placeholder = True
            else:
                raise ValueError("Unknown section: " + section)

        print(config["Settings"])

    def saveSettings(self):
        # TODO
        placeholder = True

    def getSetting(self, name):
        # TODO
        placeholder = True
