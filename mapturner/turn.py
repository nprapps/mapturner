#!/usr/bin/env python

import os
import re
import subprocess
import zipfile

import envoy
import requests
import yaml

import utils

class TurnCommand(object):
    TEMP_COUNTRIES_FILENAME = 'countries.json'
    TEMP_CITIES_FILENAME = 'cities.json'
    TEMP_RIVERS_FILENAME = 'rivers.json'
    TEMP_LAKES_FILENAME = 'lakes.json'
    TEMP_NEIGHBORS_FILENAME = 'neighbors.json'
    TEMP_TOPOJSON_FILENAME = 'temp_topo.json'

    COUNTRIES_SHP_NAME = 'ne_10m_admin_0_countries'
    CITIES_SHP_NAME = 'ne_10m_populated_places_simple'
    RIVERS_SHP_NAME = 'ne_10m_rivers_lake_centerlines'
    LAKES_SHP_NAME = 'ne_10m_lakes'

    def __init__(self):
        self.args = None
        self.config = None

    def __call__(self, args):
        self.args = args

        with open(self.args.config, 'r') as f:
            self.config = yaml.load(f)

        geojson_paths = []

        for name, layer in self.config['layers'].items():
            if 'path' not in layer:
                print 'path missing for layer %s' % name
                return

            local_path = self.get_layer(layer['path'])

            print name
            if layer['type'] == 'shp':
                geojson_path = self.process_ogr2ogr(name, layer, local_path)
                geojson_paths.append(self.process_topojson(name, layer, geojson_path))
            elif layer['type'] == 'json':
                geojson_paths.append(self.process_topojson(name, layer, local_path))
            elif layer['type'] == 'csv':
                geojson_paths.append(self.process_topojson(name, layer, local_path))
            else:
                raise Exception('Unsupported layer type %s' % layer['type'])

        self.combine_layers(geojson_paths)

    def add_argparser(self, root, parents):
        """
        Add arguments for this command.
        """
        parser = root.add_parser('turn', parents=parents)
        parser.set_defaults(func=self)

        parser.add_argument(
            dest='config', action='store',
            help='path to YAML configuration file.'
        )

        parser.add_argument(
            dest='output_path', action='store',
            help='path for TopoJSON file.'
        )

        return parser

    def get_layer(self, path):
        filename = path.split('/')[-1]
        filetype = os.path.splitext(filename)[1]

        if re.match(r'^[a-zA-Z]+://', path):
            local_path = os.path.join(utils.DATA_DIRECTORY, filename)
            if not os.path.exists(local_path):
                print 'Downloading %s...' % filename
                self.download_file(path, local_path)
        elif not os.path.exists(path):
            raise Exception('%s does not exist' % path)

        if filetype == '.zip':
            slug = os.path.splitext(filename)[0]
            output_path = os.path.join(utils.DATA_DIRECTORY, slug)
            if not os.path.exists(output_path):
                print 'Unzipping...'
                self.unzip_file(path, output_path)

            real_path = output_path
        else:
            real_path = path

        return real_path

    def download_file(self, url, local_path):
        response = requests.get(url, stream=True)

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()

    def unzip_file(self, local_path, output_path):
        """
        Unzip a local file into a specified directory.
        """
        with zipfile.ZipFile(local_path, 'r') as z:
            z.extractall(output_path)

    def process_ogr2ogr(self, name, layer, local_path):
        """
        Process shp file.
        """
        path = os.path.join(utils.DATA_DIRECTORY, '%s.json' % name)

        if os.path.exists(path):
            os.remove(path)

        ogr2ogr_cmd = ['ogr2ogr', '-f', 'GeoJSON', '-clipsrc', self.config['bbox']]

        if 'where' in layer:
            ogr2ogr_cmd.extend(['-where', '"%s"' % layer['where']])

        ogr2ogr_cmd.extend([path, local_path])

        r = envoy.run(' '.join(ogr2ogr_cmd))

        if r.std_err:
            print r.std_err

        return path

    def process_topojson(self, name, layer, path):
        topo_cmd = ['topojson', '-o', path]

        if 'id-property' in layer:
            topo_cmd.extend(['--id-property', layer['id-property']])

        if 'properties' in layer:
            topo_cmd.extend(['-p', ','.join(layer['properties'])])

        topo_cmd.extend(['--', path])

        print ' '.join(topo_cmd)

        s = envoy.run(' '.join(topo_cmd))

        if s.std_err:
            print s.std_err

        return path

    def combine_layers(self, paths):
        """
        Combine data layers into a single topojson file.
        """

        r = envoy.run('topojson -o %(output_path)s --bbox -p -- %(paths)s' % {
            'output_path': self.args.output_path,
            'paths': ' '.join(paths)
        })

        if r.std_err:
            print r.std_err