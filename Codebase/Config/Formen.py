from Config.Einstellung import Einstellung


class Formen(Einstellung):

    FORM_CIRCLE = "Kreis"
    FORM_RECTANGLE = "Rechteck"

    def __init__(self, form=FORM_RECTANGLE):
        self.form = form if self.testValue(form) else self.FORM_RECTANGLE

    def getName(self):
        return "BubbleView:Formen"

    def getValue(self):
        return self.form

    def testValue(self, value):
        if isinstance(value, str):
            if value == self.FORM_CIRCLE or value == self.FORM_RECTANGLE:
                return True
        return False
