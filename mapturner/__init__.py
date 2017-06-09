#!/usr/bin/env python

import argparse
import os
import re
import shutil
import sys
import zipfile

import envoy
import requests
from tqdm import tqdm
import yaml


ROOT_DIRECTORY = os.path.expanduser('~/.mapturner')
DATA_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'data')
TEMP_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'tmp')

SUPPORTED_FILE_TYPES = ['shp', 'json', 'csv']

VRT_TEMPLATE = """
<OGRVRTDataSource>
    <OGRVRTLayer name="%(name)s">
        <SrcDataSource>%(source)s</SrcDataSource>
        <GeometryType>wkbPoint</GeometryType>
        <LayerSRS>WGS84</LayerSRS>
        <GeometryField encoding="PointFromColumns" x="%(longitude)s" y="%(latitude)s"/>
    </OGRVRTLayer>
</OGRVRTDataSource>
"""

class MapTurner(object):
    """
    A command line utility for generating data for locator maps.
    """
    def __init__(self):
        """
        Setup and parse command line arguments.
        """
        self._install_exception_handler()

        self.argparser = argparse.ArgumentParser(
            description='A command line utility for generating data for locator maps.'
        )

        self.argparser.add_argument(
            dest='config', action='store',
            help='Path to YAML configuration file.'
        )

        self.argparser.add_argument(
            dest='output_path', action='store',
            help='Path to save save TopoJSON file.'
        )

        self.argparser.add_argument(
            '-r', '--redownload',
            dest='redownload', action='store_true',
            help='Redownload all cached files from urls.'
        )

        self.argparser.add_argument(
            '-v', '--verbose',
            dest='verbose', action='store_true',
            help='Print detailed tracebacks when errors occur.'
        )

        self.args = self.argparser.parse_args()

        # Verify mapturner directories exists
        if not os.path.exists(DATA_DIRECTORY):
            os.makedirs(DATA_DIRECTORY)

        if not os.path.exists(TEMP_DIRECTORY):
            os.makedirs(TEMP_DIRECTORY)

        # Load configuration file
        with open(self.args.config, 'r') as f:
            self.config = yaml.load(f)

        geojson_paths = []

        # Process layers
        for name, layer in self.config['layers'].items():
            if 'path' not in layer:
                raise ValueError('Path missing for layer: %s\n' % name)
                return

            layer_path = self.get_real_layer_path(layer['path'])

            sys.stdout.write('Layer: %s\n' % name)

            if layer['type'] not in SUPPORTED_FILE_TYPES:
                raise ValueError('Unsupported layer type: %s\n' % layer['type'])

            if layer['type'] in ['shp', 'json']:
                input_path = layer_path
            elif layer['type'] == 'csv':
                input_path = self.create_vrt(name, layer_path, layer)

            geojson_path = self.process_ogr2ogr(name, layer, input_path)
            geojson_paths.append(self.process_topojson(name, layer, geojson_path))

        # Merge layers
        self.merge(geojson_paths)

        shutil.rmtree(TEMP_DIRECTORY)

    def _install_exception_handler(self):
        """
        Installs a replacement for sys.excepthook, which handles pretty-printing uncaught exceptions.
        """
        def handler(t, value, traceback):
            if self.args.verbose:
                sys.__excepthook__(t, value, traceback)
            else:
                sys.stderr.write('%s\n' % str(value).encode('utf-8'))

        sys.excepthook = handler

    def get_real_layer_path(self, path):
        """
        Get the path the actual layer file.
        """
        filename = path.split('/')[-1]
        local_path = path
        filetype = os.path.splitext(filename)[1]

        # Url
        if re.match(r'^[a-zA-Z]+://', path):
            local_path = os.path.join(DATA_DIRECTORY, filename)

            if not os.path.exists(local_path):
                sys.stdout.write('* Downloading %s...\n' % filename)
                self.download_file(path, local_path)
            elif self.args.redownload:
                os.remove(local_path)

                sys.stdout.write('* Redownloading %s...\n' % filename)
                self.download_file(path, local_path)
        # Non-existant file
        elif not os.path.exists(local_path):
            raise Exception('%s does not exist' % local_path)

        real_path = path

        # Zip files
        if filetype == '.zip':
            slug = os.path.splitext(filename)[0]
            real_path = os.path.join(DATA_DIRECTORY, slug)

            if not os.path.exists(real_path):
                sys.stdout.write('* Unzipping...\n')
                self.unzip_file(local_path, real_path)

        return real_path

    def download_file(self, url, local_path):
        """
        Download a file from a remote host.
        """
        response = requests.get(url, stream=True)

        with open(local_path, 'wb') as f:
            for chunk in tqdm(response.iter_content(chunk_size=1024), unit='KB'):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()

    def unzip_file(self, zip_path, output_path):
        """
        Unzip a local file into a specified directory.
        """
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(output_path)

    def create_vrt(self, layer_name, layer_path, layer):
        vrt_path = os.path.join(TEMP_DIRECTORY, '%s.vrt' % layer_name)

        vrt_body = VRT_TEMPLATE % {
            'name': layer_name,
            'source': layer_path,
            'latitude': layer.get('latitude', 'latitude'),
            'longitude': layer.get('longitude', 'longitude')
        }

        with open(vrt_path, 'w') as f:
            f.write(vrt_body)

        return vrt_path

    def process_ogr2ogr(self, name, layer, input_path):
        """
        Process a layer using ogr2ogr.
        """
        output_path = os.path.join(TEMP_DIRECTORY, '%s.json' % name)

        if os.path.exists(output_path):
            os.remove(output_path)

        ogr2ogr_cmd = [
            'ogr2ogr',
                '-f', 'GeoJSON',
                '-clipsrc', self.config['bbox']
        ]

        if 'where' in layer:
            ogr2ogr_cmd.extend([
                '-where', '"%s"' % layer['where']
            ])

        ogr2ogr_cmd.extend([
            output_path,
            input_path
        ])

        sys.stdout.write('* Running ogr2ogr\n')

        if self.args.verbose:
            sys.stdout.write('  %s\n' % ' '.join(ogr2ogr_cmd))

        r = envoy.run(' '.join(ogr2ogr_cmd))

        if r.status_code != 0:
            sys.stderr.write(r.std_err)

        return output_path

    def process_topojson(self, name, layer, input_path):
        """
        Process layer using topojson.
        """
        output_path = os.path.join(TEMP_DIRECTORY, '%s.topojson' % name)

        # Use local topojson binary
        topojson_binary = 'node_modules/bin/topojson'

        if not os.path.exists(topojson_binary):
            # try with global topojson binary
            topojson_binary = 'topojson'

        topo_cmd = [
            topojson_binary,
            '-o', output_path
        ]

        if 'id-property' in layer:
            topo_cmd.extend([
                '--id-property', layer['id-property']
            ])

        if layer.get('all-properties', False):
            topo_cmd.append('-p')
        elif 'properties' in layer:
            topo_cmd.extend([
                '-p', ','.join(layer['properties'])
            ])

        topo_cmd.extend([
            '--',
            input_path
        ])

        sys.stdout.write('* Running TopoJSON\n')

        if self.args.verbose:
            sys.stdout.write('  %s\n' % ' '.join(topo_cmd))

        r = envoy.run(' '.join(topo_cmd))

        if r.status_code != 0:
            sys.stderr.write(r.std_err)

        return output_path

    def merge(self, paths):
        """
        Merge data layers into a single topojson file.
        """

        # Use local topojson binary
        topojson_binary = 'node_modules/bin/topojson'

        if not os.path.exists(topojson_binary):
            # try with global topojson binary
            topojson_binary = 'topojson'

        merge_cmd = '%(binary)s -o %(output_path)s --bbox -p -- %(paths)s' % {
            'output_path': self.args.output_path,
            'paths': ' '.join(paths),
            'binary': topojson_binary
        }

        sys.stdout.write('Merging layers\n')

        if self.args.verbose:
            sys.stdout.write('  %s\n' % merge_cmd)

        r = envoy.run(merge_cmd)

        if r.status_code != 0:
            sys.stderr.write(r.std_err)


def _main():
    MapTurner()

if __name__ == "__main__":
    _main()
