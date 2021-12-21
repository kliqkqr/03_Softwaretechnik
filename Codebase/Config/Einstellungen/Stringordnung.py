from Config.Einstellungen.Einstellung import Einstellung


class Stringordnung(Einstellung):

    NAME = "CodeCharts:Stringordnung"
    DEFAULT_RANDOM = True

    def __init__(self, randomisiert=DEFAULT_RANDOM):
        self.randomisiert = randomisiert if self.testValue(randomisiert) else self.DEFAULT_RANDOM

    def getName(self):
        return self.NAME

    def getValue(self):
        return self.randomisiert

    def testValue(self, value):
        return isinstance(value, bool)

    def load(self, data):
        self.randomisiert = data
        return True

