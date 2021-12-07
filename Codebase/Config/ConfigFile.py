import pathlib


class ConfigFile:

    def __init__(self, path=None):
        if path is None:
            self.path = pathlib.Path().resolve() / 'ConfigFile.txt'
        else:
            self.path = path

        config_file = pathlib.Path(self.path)
        if not config_file.exists():
            raise FileNotFoundError("The provided path does not lead to an existing file!")


    def loadSettings(self):
        pass

    def saveSettings(self):
        pass

    def getSetting(self, name):
        pass
