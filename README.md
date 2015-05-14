mapturner
=========

A command line utility for generating topojson from various data sources.

Important links:

* Repository:           https://github.com/nprapps/mapturner
* Issues:               https://github.com/nprapps/mapturner/issues

Install
-------

```
pip install mapturner
```

You will also need the following non-Python dependencies installed:
Requirements:

* GDAL (ogr2ogr)
* topojson

Usage
-----

Define a YAML configuration file, for example:

```
bbox: '77.25 24.28 91.45 31.5'
layers:
    countries:
        type: 'shp'
        path: 'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'
        id-property: 'NAME'
        properties:
            - 'country=NAME'
    quakes:
        type: 'csv'
        path: 'examples/nepal.csv'
```

Then run it!

```
mapturner input.yaml output.json
```

The output will be a topojson file containing topo equivalents of all the input layers.
