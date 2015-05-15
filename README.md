mapturner
=========

A command line utility for generating topojson from various data sources.

Important links:

* Repository:           https://github.com/nprapps/mapturner
* Issues:               https://github.com/nprapps/mapturner/issues

Install
-------

```she
pip install mapturner
```

You will also need the following non-Python dependencies installed:
Requirements:

* GDAL (ogr2ogr)
* topojson

Usage
-----

Define a YAML configuration file, for example:

```yaml
bbox: '77.25 24.28 91.45 31.5'
layers:
    countries:
        type: 'shp'
        path: 'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'
        id-property: 'NAME'
        properties:
            - 'country=NAME'

    cities:
        type: 'shp'
        path: 'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_populated_places_simple.zip'
        id-property: 'name'
        properties:
            - 'featurecla'
            - 'city=name'
        where: adm0name = 'Nepal' AND scalerank < 8

    quakes:
        type: 'csv'
        path: 'examples/nepal.csv'
```

Then run it!

```sh
mapturner input.yaml output.json
```

How it works
------------

For each layer defined in the configuration file:

* If path is a URL the file will be downloaded and cached.
* If path is zipped it will be unzipped.
* If the layer type is `shp` it will be clipped to the specified bounding box (using ogr2ogr).
* If the layer type is `shp` and a `where` attribute is specified, the layer will be filtered by that pseudo-SQL clause.
* All fields in the layer *not* specified in the `properties` array will be removed.
* The layer will be converted to topojson (a form of compression).

After each layer has been processed they will be concatenated into a single topojson file. Each layer's key name will be used to identify it in the output.

Notes
-----

The following layer types are currently supported:

* shp
* json
* csv

For a complete explanation of how the `id-property` and `properties` fields work see the [topojson documentation](https://github.com/mbostock/topojson/wiki/Command-Line-Reference).
