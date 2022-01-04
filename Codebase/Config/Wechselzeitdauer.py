from Config.Einstellung import Einstellung


class Wechselzeitdauer(Einstellung):
    DEFAULT_DAUER = 2
    NAME = "CodeCharts:Wechselzeitdauer"

    def __init__(self, dauer=DEFAULT_DAUER):
        if self.testValue(dauer):
            self.dauer = dauer              # Dauer des Wechsels in Sekunden
        else:
            self.dauer = self.DEFAULT_DAUER

    def getName(self):
        return self.NAME

    def getValue(self):
        return self.dauer

    def testValue(self, value):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value > 0:
                return True
        return False
