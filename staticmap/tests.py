from unittest import TestCase

from staticmap import StaticMap


class LonLatConversionTest(TestCase):
    def testLon(self):
        for lon in range(-180, 180, 20):
            for zoom in range(0, 10):
                x = StaticMap._lon_to_x(lon, zoom)
                l = StaticMap._x_to_lon(x, zoom)
                self.assertAlmostEqual(lon, l, places=5)

    def testLat(self):
        for lat in range(-89, 89, 2):
            for zoom in range(0, 10):
                y = StaticMap._lat_to_y(lat, zoom)
                l = StaticMap._y_to_lat(y, zoom)
                self.assertAlmostEqual(lat, l, places=5)
