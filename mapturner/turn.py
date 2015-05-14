#!/usr/bin/env python

from collections import OrderedDict
import json
import os

class TurnCommand(object):
    def __init__(self):
        self.args = None
        self.config = None
        self.service = None

    def __call__(self, args):
        self.args = args

        # TKTK

    def add_argparser(self, root, parents):
        """
        Add arguments for this command.
        """
        parser = root.add_parser('turn', parents=parents)
        parser.set_defaults(func=self)

        parser.add_argument(
            '--auth',
            dest='auth', action='store',
            help='Path to the authorized credentials file (analytics.dat).'
        )

        return parser
