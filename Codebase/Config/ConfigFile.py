import pathlib
import yaml
import os
from shutil import copyfile  # used for cloning the default config

from Config.Einstellungen import Formen, Wechselzeitdauer, Formengroesse, Rastergroesse, Stringordnung, Filter

# Implemented for the YAML standard
from Config.Einstellungen.StandardEinstellung import StandardEinstellung
from Config.Sektion import Sektion


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
        self.settings = Sektion("Settings")
        self.database = Sektion("Database")
        self.settings.addSetting(
            Filter.Filter(), Formen.Formen(), Formengroesse.Formengroesse(), Rastergroesse.Rastergroesse(),
            Stringordnung.Stringordnung(), Wechselzeitdauer.Wechselzeitdauer())
        self.database.addSetting(StandardEinstellung("host"), StandardEinstellung("user"), StandardEinstellung("pass"))

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
        for section_name in config:
            section = None
            if self.settings.getName() == section_name:
                section = self.settings
            elif self.database.getName() == section_name:
                section = self.database
            else:
                raise ValueError("Unknown section: " + section)

            # Iterate over the fields and check for available setting objects
            for field in config[section_name]:
                value = config[section_name][field]
                setting = section.getSetting(field)
                if setting is not None:
                    setting.loadYML(value)

    def saveSettings(self):
        # Check if the file exists
        config_file = pathlib.Path(self.path)
        if not config_file.exists():
            raise FileNotFoundError("The provided path does not lead to an existing file!")

        # Create and fill config dictionary
        config = {}
        sections = [self.settings, self.database]

        for section in sections:
            yaml_section = {}
            for setting in section.getSettings():
                yaml_section = setting.saveYML(yaml_section)
            config.update({section.getName(): yaml_section})

        print(config)
        # Save data
        with open(self.path, "w") as ymlfile:
            yaml.dump(config, ymlfile)

    def getSetting(self, name):
        return self.settings.getSetting(name)
