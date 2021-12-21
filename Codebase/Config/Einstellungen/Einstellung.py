from abc import ABC, abstractmethod


class Einstellung(ABC):

    TEST = "ABC"
    @abstractmethod
    def getName(self):
        pass

    @abstractmethod
    def getValue(self):
        pass

    @abstractmethod
    def testValue(self, value):
        pass

    def loadYML(self, data):
        if not self.testValue(data):
            return False
        return self.load(data)

    @abstractmethod
    def load(self, data):
        pass

    def saveYML(self, yaml_section):
        yaml_section[self.getName()] = self.getValue()
        return yaml_section

    def matches(self, key_name):
        return self.getName() == key_name
