import unittest

from Config.ConfigFile import ConfigFile
from Config.Einstellungen.Einstellung import Einstellung
from Config.Einstellungen.Filter import Filter
from Config.Einstellungen.Formengroesse import Formengroesse
from Config.Einstellungen.Rastergroesse import Rastergroesse
from Config.Einstellungen.Stringordnung import Stringordnung
from Config.Einstellungen.Formen import Formen
from Config.Einstellungen.Wechselzeitdauer import Wechselzeitdauer


class ConfigTest(unittest.TestCase):

    def test_setting(self):
        with self.assertRaises(TypeError):
            einstellung = Einstellung()

    def test_formen(self):
        formen_setting_default = Formen()
        self.assertEqual(formen_setting_default.getName(), 'BubbleView:Formen')
        self.assertEqual(formen_setting_default.getValue(), 'Rechteck')

        formen_setting_init = Formen("Blabla")
        self.assertEqual(formen_setting_init.getValue(), 'Rechteck')
        self.assertEqual(formen_setting_init.testValue('Rechteck'), True)
        self.assertEqual(formen_setting_init.testValue('Kreis'), True)
        self.assertEqual(formen_setting_init.testValue('Dreieck'), False)

    def test_filter(self):
        filter_setting = Filter(5)
        self.assertEqual(filter_setting.getName(), 'BubbleView:Filter')
        self.assertEqual(filter_setting.getValue(), [5, 'Gaussian'])
        self.assertEqual(filter_setting.testValue([10, 'Linear Bewegung']), True)
        self.assertEqual(filter_setting.testValue(5), True)
        self.assertEqual(filter_setting.testValue(-1000), False)
        self.assertEqual(filter_setting.testValue(3.141), False)
        self.assertEqual(filter_setting.testValue('Pixelize'), True)
        self.assertEqual(filter_setting.testValue('Nonlinear'), False)
        self.assertEqual(filter_setting.testValue([-5, 'Linear Bewegung']), False)
        self.assertEqual(filter_setting.testValue([5, 'Nonlinear']), False)

    def test_wechselzeitdauer(self):
        wechseldauer_setting = Wechselzeitdauer()
        self.assertEqual(wechseldauer_setting.getName(), 'CodeCharts:Wechselzeitdauer')
        self.assertEqual(wechseldauer_setting.testValue(10), True)
        self.assertEqual(wechseldauer_setting.testValue(-1), False)
        self.assertEqual(wechseldauer_setting.testValue(5.54), True)

    def test_formengroesse(self):
        size_setting = Formengroesse()
        self.assertEqual(size_setting.getName(), 'BubbleView:Formengroesse')
        self.assertEqual(size_setting.testValue(10), True)
        self.assertEqual(size_setting.testValue(-1), False)
        self.assertEqual(size_setting.testValue(5.54), False)

    def test_rastergroesse(self):
        raster_setting = Rastergroesse()
        self.assertEqual(raster_setting.getName(), 'CodeCharts:Rastergroesse')
        self.assertEqual(raster_setting.getValue(), [10, 10])
        raster_setting = Rastergroesse(2, 4)
        self.assertEqual(raster_setting.getValue(), [2, 4])
        self.assertEqual(raster_setting.testValue(-5), False)
        self.assertEqual(raster_setting.testValue(0), False)
        self.assertEqual(raster_setting.testValue([4, 4]), True)
        self.assertEqual(raster_setting.testValue(5), True) # Einzelne Laengenangaben koennen auch getestet werden
        self.assertEqual(raster_setting.testValue([-4, 4]), False)

    def test_stringordnung(self):
        stringord_setting = Stringordnung()
        self.assertEqual(stringord_setting.getName(), 'CodeCharts:Stringordnung')
        self.assertEqual(stringord_setting.getValue(), True)
        self.assertEqual(stringord_setting.testValue(10), False)
        self.assertEqual(stringord_setting.testValue('abc'), False)
        self.assertEqual(stringord_setting.testValue(False), True)

    def test_config(self):
        with self.assertRaises(FileNotFoundError):
            config = ConfigFile("blabla") # wrong path

        config = ConfigFile() # Standard path to the current directory

        config.loadSettings()
        size = config.getSetting('BubbleView:Formengroesse')
        self.assertTrue(isinstance(size, int))
        self.assertTrue(size > 0)


if __name__ == '__main__':
    unittest.main()