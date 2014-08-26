import unittest
from floodestimation.catchment import Catchment


class TestCatchmentQmed(unittest.TestCase):
    def test_channel_width_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        self.assertEqual(catchment.qmed_from_channel_width(), 0.182)

    def test_channel_width_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 2.345
        self.assertEqual(round(catchment.qmed_from_channel_width(), 4), 0.9839)

    def test_channel_width_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 50
        self.assertEqual(round(catchment.qmed_from_channel_width(), 4), 420.7576)

    def test_channel_no_width(self):
        catchment = Catchment("Aberdeen", "River Dee")
        with self.assertRaises(Exception):
            qmed = catchment.qmed_from_channel_width()

    def test_channel_area_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_area = 1
        self.assertEqual(catchment.qmed_from_channel_area(), 1.172)

    def test_channel_area_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_area = 2.345
        self.assertEqual(round(catchment.qmed_from_channel_area(), 4), 2.6946)

    def test_channel_area_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_area = 100
        self.assertEqual(round(catchment.qmed_from_channel_area(), 4), 81.2790)

    def test_channel_no_width(self):
        catchment = Catchment("Aberdeen", "River Dee")
        with self.assertRaises(Exception):
            qmed = catchment.qmed_from_channel_area()