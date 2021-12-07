import unittest

from Speichermedium.Speicher import Speicher
from datetime import datetime
from PIL import Image, ImageChops


class SpeicherTest(unittest.TestCase):

    def test_save_data(self):
        speicher = Speicher()

        timestamp = datetime.now()
        image_id = 1
        success = True
        eye_gaze_coordinates = [150, 235]

        id = speicher.speicherCodeChartTest(timestamp, success, image_id, eye_gaze_coordinates)

        if id < 0:
            self.fail("Could'nt save data")

    def test_load_data(self):
        speicher = Speicher()

        id = 1
        result = speicher.loadCodeChartTest(id)

        if not result:
            self.fail("Could'nt load data")

        self.assertEqual(result[1], True)
        self.assertEqual(result[2], 1)
        self.assertEqual(result[3], [150, 235])


    def test_image(self):
        speicher = Speicher()

        exp_img = Image.open('demo_image.jpg')
        id = speicher.speicherBild(exp_img)

        self.assertTrue(id > 0)

        # Load image again
        same_img = speicher.ladeBild(id)
        img_difference = ImageChops.difference(exp_img, same_img)
        self.assertFalse(img_difference.getbbox())



