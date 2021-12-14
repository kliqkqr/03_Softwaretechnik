from abc import ABC, abstractmethod


class Einstellung(ABC):

    @abstractmethod
    def getName(self):
        pass

    @abstractmethod
    def getValue(self):
        pass

    @abstractmethod
    def testValue(self, value):
        pass

    #@abstractmethod
    #def loadYML(self, data):
    #    pass

    def matches(self, key_name):
        return self.getName() == key_name
