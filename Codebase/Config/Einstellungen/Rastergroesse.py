from Config.Einstellungen.Einstellung import Einstellung


class Rastergroesse(Einstellung):

    NAME = "CodeCharts:Rastergroesse"
    DEFAULT_WIDTH = 10
    DEFAULT_HEIGHT = 10

    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        self.width = width if self.testValue(width) else self.DEFAULT_WIDTH
        self.height = height if self.testValue(height) else self.DEFAULT_HEIGHT

    def getName(self):
        return self.NAME

    def getValue(self):
        return [self.width, self.height]

    def testValue(self, value):
        if isinstance(value, list):
            if len(value) != 2:
                return False
            return self.testValue(value[0]) and self.testValue(value[1])

        if isinstance(value, int) and not isinstance(value, bool):
            if value > 0:
                return True
        return False

    def load(self, data):
        self.width = data[0]
        self.height = data[1]
        return True
