

class Sektion:

    def __init__(self, name):
        self.name = name
        self.settings = []

    def getName(self):
        return self.name

    def addSetting(self, *settings):
        for setting in settings:
            if self.hasSetting(setting.getName()):
                raise ValueError("There is already a setting present with this name")

            self.settings.append(setting)

    def hasSetting(self, name):
        return self.getSetting(name) is not None

    def getSetting(self, name):
        for setting in self.settings:
            if setting.getName() == name:
                return setting
        return None

    def getSettings(self):
        return self.settings
