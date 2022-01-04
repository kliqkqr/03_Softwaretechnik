from Config.Einstellung import Einstellung


class Stringordnung(Einstellung):

    DEFAULT_SORTED = True
    NAME = "CodeCharts:Stringordnung"

    def __init__(self, sort=DEFAULT_SORTED):
        self.sorted = sort if self.testValue(sort) else self.DEFAULT_SORTED

    def getName(self):
        return self.NAME

    def getValue(self):
        return self.sorted

    def testValue(self, value):
        return isinstance(value, bool)

    def isSorted(self):
        return self.getValue()
