# mapturner

A command line utility for generating consolidated [TopoJSON](https://github.com/mbostock/topojson/wiki/Command-Line-Reference) from various data sources. Used for making fast vector maps with D3.

Important links:

* Repository:           https://github.com/nprapps/mapturner
* Issues:               https://github.com/nprapps/mapturner/issues

## Install

You will need to have the following non-Python dependencies installed:

* ogr2ogr (GDAL): `brew install ogr2ogr`
* topojson@1.6.27: (topojson 2+ does not work)

mapturner itself can be installed with pip:

```
pip install mapturner
```

Note: Since `mapturner` relies on topojson 1.x (old version of topojson), we recommend installing this version of topojson inside your project root folder by running:

```
npm install -g topojson@1.6.27 --prefix node_modules
```

To install topojson@1.6.27 globally instead run:

```
npm install -g topojson@1.6.27
```

`mapturner` will search first for the topojson binaries installed within the project and fallback to searching the topojson binary on your $PATH.


Developer install process:

```
git clone git://github.com/nprapps/mapturner.git
cd mapturner
mkvirtualenv mapturner

pip install -r requirements.txt

python setup.py develop
```

## Usage

Define a YAML configuration file, such as the following example. The complete list of valid options is further on in this documentation.

```
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

Then run it!

```
mapturner input.yaml output.json
```

The following layer types are currently supported:

* ESRI Shapefile (`shp`)
* GeoJSON or TopoJSON (`json`)
* CSV (`csv`)

## How it works

For each layer defined in the configuration file:

* If path is a URL the file will be downloaded and cached locally. (It will not be redownloaded on subsequent runs.)
* If path is to a zipped file it will be unzipped.
* All layers will be clipped to the specified bounding box (using ogr2ogr).
* For each layer, if a `where` attribute is specified, the layer data will be filtered by that clause.
* For each layer, all fields in the layer *not* specified in the `properties` array will be removed (to reduce file size), unless `all-properties` is specified, in which case all will be kept.
* For each layer, if an `id-property` is set, data from that property will be set as the identifier for the features in the layer.
* The layer will be converted to [TopoJSON](https://github.com/mbostock/topojson/wiki/Command-Line-Reference).

After each layer has been processed all of them will be concatenated into a single TopoJSON file. Each layer's key name will be used to identify it in the output.

## Complete list of configuration options

For all layer types:

* `type`: The type of layer. Valid types are `shp`, `json` (GeoJSON or TopoJSON), and `csv`. **(Required)**
* `path`: The path (relative or absolute) to the layer data file. **(Required)**
* `id-property`: A property from the data file to use as the unique identifier for features. See also, [the TopoJSON command-line documentation](https://github.com/mbostock/topojson/wiki/Command-Line-Reference).
* `properties`: A list of properties from the data to be kept in the output. All other properties are dropped.
* `all-properties`: If true, then all properties are kept for this layer.
* `where`: A SQL-like query predicate that will filter the feature data. This This uses exactly the same query syntax as [ogr2ogr](http://www.gdal.org/ogr2ogr.html).

CSV layers only:

* `latitude`: The name of a column in the data containing the latitude of the point/feature.
* `longitude`: The name of a column in the data containing the longitude of the point/feature.

## Cached data

Cached shapefiles are stored in `~/.mapturner`. You may wish to clear this folder periodically to free up space and ensure updated shapefiles are redownloaded.
