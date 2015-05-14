#!/usr/bin/env python

import os
import subprocess

import envoy

import utils

class TurnCommand(object):
    TEMP_COUNTRIES_FILENAME = 'temp_countries.json'
    TEMP_CITIES_FILENAME = 'temp_cities.json'
    TEMP_NEIGHBORS_FILENAME = 'temp_neighbors.json'
    COUNTRIES_SHP_NAME = 'ne_10m_admin_0_countries'
    CITIES_SHP_NAME = 'ne_10m_populated_places_simple'

    def __init__(self):
        self.args = None
        self.config = None
        self.service = None

    def __call__(self, args):
        self.args = args

        self.convert_countries()
        self.convert_cities()

    def add_argparser(self, root, parents):
        """
        Add arguments for this command.
        """
        parser = root.add_parser('turn', parents=parents)
        parser.set_defaults(func=self)

        parser.add_argument(
            dest='xmin', action='store',
            help='Minimum X value of bounding box.'
        )

        parser.add_argument(
            dest='ymin', action='store',
            help='Minimum Y value of bounding box.'
        )

        parser.add_argument(
            dest='xmax', action='store',
            help='Maximum X value of bounding box.'
        )

        parser.add_argument(
            dest='ymax', action='store',
            help='Maximum Y value of bounding box.'
        )

        parser.add_argument(
            '-c', '--country',
            dest='country', action='store',
            help='Country to include details for.'
        )

        parser.add_argument(
            '--scalerank',
            dest='scalerank', action='store', type=int, default=8,
            help='Scalerank for highlighted country (or all countries if none highlighted).'
        )

        parser.add_argument(
            '--neighbor-scalerank',
            dest='neighbor_scalerank', action='store', type=int, default=2,
            help='Scalerank for neighboring countries (if one is highlighted).'
        )

        return parser

    def convert_countries(self):
        path = os.path.join(utils.DATA_DIRECTORY, self.TEMP_COUNTRIES_FILENAME)

        if os.path.exists(path):
            os.remove(path)

        r = envoy.run('ogr2ogr -f GeoJSON -clipsrc %(xmin)s %(ymin)s %(xmax)s %(ymax)s %(output_path)s %(input_path)s' % {
            'xmin': self.args.xmin,
            'ymin': self.args.ymin,
            'xmax': self.args.xmax,
            'ymax': self.args.ymax,
            'output_path': path,
            'input_path': os.path.join(utils.DATA_DIRECTORY, '%s/%s.shp' % (self.COUNTRIES_SHP_NAME, self.COUNTRIES_SHP_NAME))
        })

    def convert_cities(self):
        """
        Convert city data to geojson, optionally focusing on a specific country.
        """
        if self.args.country:
            path = os.path.join(utils.DATA_DIRECTORY, self.TEMP_CITIES_FILENAME)

            if os.path.exists(path):
                os.remove(path)

            # Focused country
            r = envoy.run('ogr2ogr -f GeoJSON -clipsrc %(xmin)s %(ymin)s %(xmax)s %(ymax)s %(output_path)s -where %(where)s %(input_path)s' % {
                'xmin': self.args.xmin,
                'ymin': self.args.ymin,
                'xmax': self.args.xmax,
                'ymax': self.args.ymax,
                'output_path': path,
                'where': '"adm0name = \'%s\' AND scalerank < %i"' % (self.args.country, self.args.scalerank),
                'input_path': os.path.join(utils.DATA_DIRECTORY, '%s/%s.shp' % (self.CITIES_SHP_NAME, self.CITIES_SHP_NAME)),
            })

            print r.std_err

            path = os.path.join(utils.DATA_DIRECTORY, self.TEMP_NEIGHBORS_FILENAME)

            if os.path.exists(path):
                os.remove(path)

            # Neighbors
            r = envoy.run('ogr2ogr -f GeoJSON -clipsrc %(xmin)s %(ymin)s %(xmax)s %(ymax)s %(output_path)s -where %(where)s %(input_path)s' % {
                'xmin': self.args.xmin,
                'ymin': self.args.ymin,
                'xmax': self.args.xmax,
                'ymax': self.args.ymax,
                'output_path': path,
                'where': '"adm0name != \'%s\' AND scalerank < %i"' % (self.args.country, self.args.neighbor_scalerank),
                'input_path': os.path.join(utils.DATA_DIRECTORY, '%s/%s.shp' % (self.CITIES_SHP_NAME, self.CITIES_SHP_NAME)),
            })
        else:
            path = os.path.join(utils.DATA_DIRECTORY, self.TEMP_CITIES_FILENAME)

            if os.path.exists(path):
                os.remove(path)

            r = envoy.run('ogr2ogr -f GeoJSON -clipsrc %(xmin)s %(ymin)s %(xmax)s %(ymax)s %(output_path)s -where %(where)s %(input_path)s' % {
                'xmin': self.args.xmin,
                'ymin': self.args.ymin,
                'xmax': self.args.xmax,
                'ymax': self.args.ymax,
                'output_path': path,
                'where': '"scalerank < %i"' % self.args.scalerank,
                'input_path': os.path.join(utils.DATA_DIRECTORY, '%s/%s.shp' % (self.CITIES_SHP_NAME, self.CITIES_SHP_NAME)),
            })
