from io import BytesIO
from math import log, tan, cos, pi, floor, ceil

import requests
from PIL import Image, ImageDraw


class Line:
    def __init__(self, coords, color, width):
        """
        Line that can be drawn in a static map

        :param coords: an iterable of lon-lat pairs, e.g. ((0.0, 0.0), (175.0, 0.0), (175.0, -85.1))
        :type coords: list
        :param color: color suitable for PIL / Pillow
        :type color: str
        :param width: width in pixel
        :type width: int
        """
        self.coords = coords
        self.color = color
        self.width = width

    @property
    def extent(self):
        """
        calculate the coordinates of the envelope / bounding box: (min_lon, min_lat, max_lon, max_lat)

        :rtype: tuple
        """
        return (
            min((c[0] for c in self.coords)),
            min((c[1] for c in self.coords)),
            max((c[0] for c in self.coords)),
            max((c[1] for c in self.coords)),
        )


class Marker:
    def __init__(self, coord, color, width):
        """
        :param coord: a lon-lat pair, eg (175.0, 0.0)
        :type coord: tuple
        :param color: color suitable for PIL / Pillow
        :type color: str
        :param width: marker width
        :type width: int
        """
        self.coord = coord
        self.color = color
        self.width = width


class StaticMap:
    # def __init__(self, width: int, height: int, padding: int=0, url_template: str="http://a.tile.komoot.de/komoot/{z}/{x}/{y}.png", tile_size: int=256):
    def __init__(self, width, height, padding=0, url_template="http://a.tile.komoot.de/komoot-2/{z}/{x}/{y}.png", tile_size=256):
        """
        :param width: map width in pixel
        :type width: int
        :param height:  map height in pixel
        :type height: int
        :param padding: min distance in pixel from map features to border of map
        :type padding: int
        :param url_template: tile URL
        :type url_template: str
        :param tile_size: the size of the map tiles in pixel
        :type tile_size: int
        """
        self.width = width
        self.height = height
        self.padding = padding
        self.url_template = url_template
        self.tile_size = tile_size

        # features
        self.markers = []
        self.lines = []

        # fields that get set when map is rendered
        self.x_center = 0
        self.y_center = 0
        self.zoom = 0

    def add_line(self, line):
        """
        :param line: line to draw
        :type line: Line
        """
        self.lines.append(line)

    def add_marker(self, marker):
        """
        :param marker: marker to draw
        :type marker: Marker
        """
        self.markers.append(marker)

    def render(self, zoom=None):
        """
        render static map with all map features that were added to map before

        :param zoom: optional zoom level, will be optimized automatically if not given.
        :type zoom: int
        :return: PIL image instance
        :rtype: Image.Image
        """

        if not self.lines and not self.markers:
            raise RuntimeError("cannot render empty map, add lines / markers first")

        # get extent of all lines
        extent = self._determine_extent()

        if zoom is None:
            self.zoom = self._calculate_zoom(extent)
        else:
            self.zoom = zoom

        # calculate center point of map
        lon_center, lat_center = (extent[0] + extent[2]) / 2, (extent[1] + extent[3]) / 2
        self.x_center = self._lon_to_x(lon_center, self.zoom)
        self.y_center = self._lat_to_y(lat_center, self.zoom)

        image = Image.new('RGB', (self.width, self.height), '#fff')

        self._draw_base_layer(image)
        self._draw_features(image)

        return image

    def _determine_extent(self):
        """ calculate common extent of all current map features """
        extents = [l.extent for l in self.lines]
        extents += [(m.coord[0], m.coord[1]) * 2 for m in self.markers]

        return (
            min(e[0] for e in extents),
            min(e[1] for e in extents),
            max(e[2] for e in extents),
            max(e[3] for e in extents)
        )

    def _calculate_zoom(self, extent):
        """
        calculate the best zoom level for given extent

        :param extent: extent in lon lat to render
        :type extent: tuple
        :return: lowest zoom level for which the entire extent fits in
        :rtype: int
        """
        for z in range(17, -1, -1):
            width = (self._lon_to_x(extent[2], z) - self._lon_to_x(extent[0], z)) * self.tile_size
            if width > (self.width - self.padding):
                continue

            height = (self._lat_to_y(extent[1], z) - self._lat_to_y(extent[3], z)) * self.tile_size
            if height > (self.height - self.padding):
                continue

            # we found first zoom that can display entire extent
            return z

        return ValueError("map dimension (width = {self.width}px, height = {self.height}px, padding = {self.padding}px) is too small for given lines".format(self=self))

    @staticmethod
    def _lon_to_x(lon, zoom):
        """
        transform longitude to tile number
        :type lon: float
        :type zoom: int
        :rtype: float
        """
        return ((lon + 180) / 360) * pow(2, zoom)

    @staticmethod
    def _lat_to_y(lat, zoom):
        """
        transform latitude to tile number
        :type lat: float
        :type zoom: int
        :rtype: float
        """
        return (1 - log(tan(lat * pi / 180) + 1 / cos(lat * pi / 180)) / pi) / 2 * pow(2, zoom)

    def _x_to_px(self, x):
        """
        transform tile number to pixel on image canvas
        :type x: float
        :rtype: float
        """
        px = (x - self.x_center) * self.tile_size + self.width / 2
        return int(round(px))

    def _y_to_px(self, y):
        """
        transform tile number to pixel on image canvas
        :type y: float
        :rtype: float
        """
        px = (y - self.y_center) * self.tile_size + self.height / 2
        return int(round(px))

    def _draw_base_layer(self, image):
        """
        :type image: Image.Image
        """
        x_min = int(floor(self.x_center - (0.5 * self.width / self.tile_size)))
        y_min = int(floor(self.y_center - (0.5 * self.height / self.tile_size)))
        x_max = int(ceil(self.x_center + (0.5 * self.width / self.tile_size)))
        y_max = int(ceil(self.y_center + (0.5 * self.height / self.tile_size)))

        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                res = requests.get(self.url_template.format(z=self.zoom, x=x, y=y))
                if res.status_code != 200:
                    raise RuntimeError("could not download tile: {}: {}".format(self.url_template.format(z=self.zoom, x=x, y=y), res.status_code))

                tile = Image.open(BytesIO(res.content))
                box = [
                    self._x_to_px(x),
                    self._y_to_px(y),
                    self._x_to_px(x + 1),
                    self._y_to_px(y + 1),
                ]
                image.paste(tile, box)

    def _draw_features(self, image):
        """
        :type image: Image.Image
        """
        # Pillow does not support anti aliasing for lines and circles
        # There is a trick to draw them on an image that is twice the size and resize it at the end before it gets merged with  the base layer

        image_lines = Image.new('RGBA', (self.width * 2, self.height * 2), (255, 0, 0, 0))
        draw = ImageDraw.Draw(image_lines)

        for line in self.lines:
            points = [(
                          self._x_to_px(self._lon_to_x(coord[0], self.zoom)) * 2,
                          self._y_to_px(self._lat_to_y(coord[1], self.zoom)) * 2,
                      ) for coord in line.coords]

            for point in points:
                # draw extra points to make the connection between lines look nice
                draw.ellipse((
                    point[0] - line.width + 1,
                    point[1] - line.width + 1,
                    point[0] + line.width - 1,
                    point[1] + line.width - 1
                ), fill=line.color)

            draw.line(points, fill=line.color, width=line.width * 2)

        for marker in self.markers:
            point = [
                self._x_to_px(self._lon_to_x(marker.coord[0], self.zoom)) * 2,
                self._y_to_px(self._lat_to_y(marker.coord[1], self.zoom)) * 2
            ]
            draw.ellipse((
                point[0] - marker.width,
                point[1] - marker.width,
                point[0] + marker.width,
                point[1] + marker.width
            ), fill=marker.color)

        image_lines = image_lines.resize((self.width, self.height), Image.ANTIALIAS)

        # merge lines with base image
        image.paste(image_lines, (0, 0), image_lines)


if __name__ == '__main__':
    map = StaticMap(300, 400, 10)
    line = Line([(13.4, 52.5), (2.3, 48.9)], 'blue', 3)
    map.add_line(line)
    image = map.render()
    image.save('map.png')
