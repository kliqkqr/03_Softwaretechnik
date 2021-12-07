import unittest 

from PIL               import Image

from Config.ConfigFile import ConfigFile
from Webcam            import Pupille, Auge, Person, Kalibrierung, Webcam, Eyetracking


def example_image():
    return Image.new('RGB', (100, 100), color = (100, 100, 100))


class WebcamTest(unittest.TestCase):
    def test_pupille(self):
        pupille_default = Pupille()
        self.assertEqual(pupille_default.posPupil(), None)

        pupille_init = Pupille((1, 2))
        self.assertEqual(pupille_init, (1, 2))

    def test_auge(self):
        auge_default = Auge()
        self.assertEqual(auge_default.posEye(), (0, 0))

        auge_init = Auge((1, 2))
        self.assertEqual(auge_init.posEye(), (1, 2))

    def test_person(self):
        person_default = Person()
        self.assertEqual(person_default.getName(), None)
        self.assertEqual(person_default.getAge(), None)

        person_init = Person("Max Mustermann", 30)
        self.assertEqual(person_init.getName(), "Max Mustermann")
        self.assertEqual(person_init.getAge(), 30)

    def test_kalibrierung(self):
        kalibrierung_default = Kalibrierung()
        self.assertEqual(kalibrierung_default.getClickedArea(), None)

        kalibrierung_init = Kalibrierung((1, 2))
        self.assertEqual(kalibrierung_init.getClickedArea(), (1, 2))

    def test_webcam(self):
        webcam_default = Webcam()
        self.assertEqual(webcam_default.visiblePerson, False)

        webcam_default.setVisibilityPerson(True)
        self.assertEqual(webcam_default.visiblePerson, True)

        webcam_image = example_image()
        webcam_default.setCurWebcamImage(webcam_image)
        self.assertEqual(webcam_default.curWebcamImage, webcam_image)

        display_image = example_image()
        webcam_default.setCurDisplayImage(display_image)
        self.assertEqual(webcam_default.curDisplayImage, display_image)

    def test_eyetracking(self):
        eyetracking_default = Eyetracking()

        webcam_image = example_image()
        eyetracking_default.curWebcamImage = webcam_image
        self.assertEqual(eyetracking_default.getWebcamImage(), webcam_image)

        display_image = example_image()
        eyetracking_default.curDisplayImage = display_image 
        self.assertEqual(eyetracking_default.getDisplayImage(), display_image)

        config_file = ConfigFile()

        try:
            eyetracking_default.loadSettings(config_file)
        except:
            self.fail('Failed')