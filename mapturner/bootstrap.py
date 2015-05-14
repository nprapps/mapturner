#!/usr/bin/env python

import os

class BootstrapCommand(object):
    def __init__(self):
        self.args = None

    def __call__(self, args):
        self.args = args

        # TKTK

    def add_argparser(self, root, parents):
        """
        Add arguments for this command.
        """
        parser = root.add_parser('bootstrap', parents=parents)
        parser.set_defaults(func=self)

        parser.add_argument(
            '--secrets',
            dest='secrets', action='store',
            help='Path to the authorization secrets file (client_secrets.json).'
        )

        return parser
