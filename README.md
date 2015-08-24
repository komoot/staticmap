# Static Map

A small, python-based library for creating map images with lines and markers.

## Example
```python
m = StaticMap(300, 400, 10)
m.add_line(Line(((13.4, 52.5), (2.3, 48.9)), 'blue', 3))
image = m.render()
image.save('map.png')
```
This will create a 300px x 400px map with a blue line drawn from Berlin to Paris.
![Map with Line from Berlin to Paris](/samples/berlin_paris.png?raw=true)


## Installation
StaticMap is a small library, all it takes is python3 and two python packages: [Pillow](https://python-pillow.github.io/) and [request](http://www.python-requests.org/). You can install them via:

```bash
pip install -r requirements.txt
```

## Usage
### Create a new map instance:

```python
map = StaticMap(width, height, padding, url_template, tile_size)
```

<dl>
  <dt>width</dt>
  <dd>width of the image in pixels</dd>

  <dt>height</dt>
  <dd>height of the image in pixels</dd>

  <dt>padding</dt>
  <dd>minimum distance in pixel between map features (lines, markers) and map border</dd>

  <dt>url_template</dt>
  <dd>the tile server URL for the map base layer, e.g. <code>http://a.tile.osm.org/{z}/{x}/{y}.png</code></dd>

  <dt>tile_size</dt>
  <dd>tile size in pixel, usually 256</dd>
</dl>

### Add a line:

```python
line = Line(coordinates, color, width))
m.add_line(line)
```

<dl>
  <dt>coordinate</dt>
  <dd>a sequence of lon/lat pairs</dd>

  <dt>color</dt>
  <dd>a color definition <a href="http://pillow.readthedocs.org/en/latest/reference/ImageColor.html#color-names">Pillow supports</a></dd>

  <dt>width</dt>
  <dd>the stroke width of the line in pixel</dd>
</dl>

### Add a map marker:

```python
marker = Marker(coordinate, color, width))
m.add_marker(marker)
```

<dl>
    <dt>coordinate</dt>
    <dd>a lon/lat pair: e.g. `(120.1, 47.3)`</dd>

    <dt>color</dt>
    <dd>a color definition <a href="http://pillow.readthedocs.org/en/latest/reference/ImageColor.html#color-names">Pillow supports</a></dd>

    <dt>width</dt>
    <dd>diameter of marker in pixel</dd>
</dl>

## Samples
### Show Position on Map
```python
map = StaticMap(200, 200, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

marker_outline = Marker((10, 47), 'white', 18)
marker = Marker((10, 47), '#0036FF', 12)

map.add_marker(marker_outline)
map.add_marker(marker)

image = map.render(zoom=5)
image.save('marker.png')
```

![Position Marker on a Map](/samples/marker.png?raw=true)

### Show Ferry Connection
```python
map = StaticMap(200, 200, 80)

coordinates = [[12.422, 45.427], [13.749, 44.885]]
line_outline = Line(coordinates, 'white', 6)
line = Line(coordinates, '#D2322D', 4)

map.add_line(line_outline)
map.add_line(line)

image = map.render()
image.save('ferry.png')
```

![Ferry Connection Shown on a Map](/samples/ferry.png?raw=true)

### Licence
StaticMap is open source and licensed under Apache License, Version 2.0

The map samples on this page are made with [OSM](http://www.osm.org) data, © [OpenStreetMap](http://www.openstreetmap.org/copyright) contributors
