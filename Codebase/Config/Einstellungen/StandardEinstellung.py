from .Einstellung import Einstellung


class StandardEinstellung(Einstellung):

    DEFAULT_STRING = None

    def __init__(self, name, value=DEFAULT_STRING):
        self.name = name
        self.value = value if self.testValue(value) else self.DEFAULT_STRING

    def getName(self):
        return self.name

    def getValue(self):
        return self.value

    def testValue(self, value):
        return isinstance(value, str)

    def load(self, data):
        self.value = data
        return True

