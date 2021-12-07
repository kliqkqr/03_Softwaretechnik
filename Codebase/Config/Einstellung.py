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
