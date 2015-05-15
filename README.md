mapturner
=========

A command line utility for generating topojson from various data sources for fast maps.

Important links:

* Repository:           https://github.com/nprapps/mapturner
* Issues:               https://github.com/nprapps/mapturner/issues

Install
-------

You will need the following non-Python dependencies installed:

* ogr2ogr (GDAL)
* topojson

User install process:

```sh
pip install mapturner
```

Developer install process:

```sh
git clone git://github.com/nprapps/mapturner.git
cd mapturner
mkvirtualenv mapturner

pip install -r requirements.txt

python setup.py develop
```

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
        all-properties: True
```

(See [test.yaml](https://github.com/nprapps/mapturner/blob/master/test.yaml) for a complete example.)

Then run it!

```sh
mapturner input.yaml output.json
```

How it works
------------

For each layer defined in the configuration file:

* If path is a URL the file will be downloaded and cached locally. (It will not be redownloaded on subsequent runs.)
* If path is to a zipped file it will be unzipped.
* If the layer type is `shp` it will be clipped to the specified bounding box (using ogr2ogr).
* If the layer type is `shp` and a `where` attribute is specified, the layer will be filtered by that clause.
* All fields in the layer *not* specified in the `properties` array will be removed (to reduce file size), unless `all-properties` is specified, in which case all will be kept.
* The layer will be converted to topojson (a form of compression).

After each layer has been processed all of them will be concatenated into a single topojson file. Each layer's key name will be used to identify it in the output.

Notes
-----

The following layer types are currently supported:

* shp
* json
* csv

For a complete explanation of how the `id-property` and `properties` fields work see the [topojson command-line documentation](https://github.com/mbostock/topojson/wiki/Command-Line-Reference).
