from Config.Einstellungen.Einstellung import Einstellung


class Formengroesse(Einstellung):

    NAME = "BubbleView:Formengroesse"
    DEFAULT_SIZE = 10 # 10px * 10px

    def __init__(self, size=DEFAULT_SIZE):
        self.size = size if self.testValue(size) else self.DEFAULT_SIZE

    def getName(self):
        return self.NAME

    def getValue(self):
        return self.size

    def testValue(self, value):
        if isinstance(value, int) and not isinstance(value, bool):
            if value > 0:
                return True
        return False

    def load(self, data):
        self.size = data
        return True
