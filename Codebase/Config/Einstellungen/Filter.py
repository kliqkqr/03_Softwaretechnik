from .Einstellung import Einstellung


class Filter(Einstellung):

    NAME = "BubbleView:Filter"
    DEFAULT_STRENGTH = 10;
    DEFAULT_TYPE = "Gaussian"
    GAUSSIAN_BLUR_FILTER = "Gaussian"
    PIXELIZE_FILTER = "Pixelize"
    LINEAR_MOVEMENT_FILTER = "Linear Bewegung"

    def __init__(self, strength=DEFAULT_STRENGTH, type=DEFAULT_TYPE):
        if not isinstance(type, str):
            type = self.DEFAULT_TYPE
        else:
            self.type = type if self.testValue(type) else self.DEFAULT_TYPE;
        self.strength = strength if self.testValue(strength) else self.DEFAULT_STRENGTH;

    def getName(self):
        return self.NAME

    def getValue(self):
        return [self.strength, self.type]

    def testValue(self, value):
        if isinstance(value, list):
            if len(value) != 2:
                return False
            return self.testValue(value[0]) and self.testValue(value[1])

        # Strength
        if isinstance(value, int) and not isinstance(value, bool):
            if value > 0:
                return True
        # Filter type
        elif isinstance(value, str):
            return value == self.GAUSSIAN_BLUR_FILTER or value == self.PIXELIZE_FILTER or value == self.LINEAR_MOVEMENT_FILTER

        return False

    def load(self, data):
        self.strength = data[0]
        self.type = data[1]
        return True

