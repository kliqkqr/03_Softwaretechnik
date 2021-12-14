from Config.Einstellung import Einstellung


class Stringordnung(Einstellung):

    DEFAULT_RANDOM = True

    def __init__(self, randomisiert=DEFAULT_RANDOM):
        self.randomisiert = randomisiert if self.testValue(randomisiert) else self.DEFAULT_RANDOM

    def getName(self):
        return "CodeCharts:Stringordnung"

    def getValue(self):
        return self.randomisiert

    def testValue(self, value):
        return isinstance(value, bool)
