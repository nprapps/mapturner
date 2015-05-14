#!/usr/bin/env python

import os
import zipfile

import requests

import utils

class BootstrapCommand(object):
    DATA_URLS = [
        'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip',
        'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_populated_places_simple.zip',
        'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_roads.zip',
        'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_1_states_provinces_lakes.zip'
    ]

    def __init__(self):
        self.args = None

    def __call__(self, args):
        self.args = args

        if not os.path.exists(utils.DATA_DIRECTORY):
            os.makedirs(utils.DATA_DIRECTORY)

        for url in self.DATA_URLS:
            local_filename = url.split('/')[-1]
            local_path = os.path.join(utils.DATA_DIRECTORY, local_filename)

            if os.path.exists(local_path):
                print 'Skipping %s (already exists)' % local_filename
                continue

            print 'Downloading %s...' % local_filename

            self.download_file(url, local_path)

            print 'Unzipping...'

            self.unzip_file(local_path)

    def add_argparser(self, root, parents):
        """
        Add arguments for this command.
        """
        parser = root.add_parser('bootstrap', parents=parents)
        parser.set_defaults(func=self)

        # parser.add_argument(
        #     '--secrets',
        #     dest='secrets', action='store',
        #     help='Path to the authorization secrets file (client_secrets.json).'
        # )

        return parser

    def download_file(self, url, local_path):
        response = requests.get(url, stream=True)

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()

    def unzip_file(self, local_path):
        filename = os.path.split(local_path)[1]
        slug = os.path.splitext(filename)[0]
        path = os.path.join(utils.DATA_DIRECTORY, slug)

        with zipfile.ZipFile(local_path, 'r') as z:
            z.extractall(path)
