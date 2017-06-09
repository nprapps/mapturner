#!/usr/bin/env python

import sys
from setuptools import setup

install_requires = [
    'requests>=2.5.0',
    'envoy>=0.0.3',
    'pyyaml>=3.11',
    'tqdm>=4.8.4'
]

setup(
    name='mapturner',
    version='0.2.1',
    description='A command line utility for compiling map data.',
    long_description=open('README.md').read(),
    author='NPR Visuals',
    author_email='nprapps@npr.org',
    url='https://github.com/nprapps/mapturner',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    packages=[
        'mapturner'
    ],
    entry_points={
        'console_scripts': [
            'mapturner = mapturner:_main'
        ]
    },
    install_requires=install_requires
)
