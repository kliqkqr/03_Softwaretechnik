import unittest
from CodeChart.Chart import Chart

class CodeChartTest(unittest.TestCase):
    
    def test_load_image(self):
        chart = Chart()
        try:
            chart.load_image()
        except TypeError:
            self.fail("Loading Image failed")
    
    def test_show_matrix(self):
        chart = Chart()
        try:
            chart.show_iamge()
        except TypeError:
            self.fail("Failed to show matrix")
    
    def test_change_matrix(self):
        chart = Chart()
        try:
            chart.change_matrix()
        except TypeError:
            self.fail("Failed to show matrix")