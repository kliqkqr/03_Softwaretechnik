import unittest
from Datenanalyse.Client import Client


class ConfigTest(unittest.TestCase):

    def test_load_data(self):
        analyse_client = Client()
        try:
            analyse_client.load_daten()
        except TypeError:
            self.fail("Couldn't load data")

    def test_load_bild(self):
        analyse_client = Client()
        try:
            analyse_client.load_bild()
        except TypeError:
            self.fail("Couldn't load image")

    def test_open(self):
        analyse_client = Client()
        with self.assertRaises(TypeError):
            analyse_client.open_tool('BubbleView')

        analyse_client.load_daten()
        analyse_client.load_bild()

        try:
            analyse_client.open_tool('BubbleView')
            analyse_client.open_tool('CodeCharts')
        except TypeError:
            self.fail("Failed")

        with self.assertRaises(TypeError):
            analyse_client.open_tool('Test')