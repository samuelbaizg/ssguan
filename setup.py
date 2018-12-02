# -*- coding: utf-8 -*-
#  Copyright 2015 www.suishouguan.com
#
#  Licensed under the Private License (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://github.com/samuelbaizg/ssguan/blob/master/LICENSE
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from codecs import open
from os import path

from setuptools import setup, find_packages

import ssguan


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'backports-abc>=0.4',
    'backports.ssl-match-hostname>=3.5.0.1',
    'certifi>=2015.11.20.1',
    'pyasn1>=0.1.9',
    'pyDes>=2.0.1',
    'pytz>=2015.7',
    'tzlocal>=1.3',
    'rsa>=3.3',
    'singledispatch>=3.4.0.3',
    'six>=1.10.0',
    'requests>=2.13.0',
    'tornado>=4.3',
    'click>=6.6',
    'futures>=3.0.5',
]


extras_require_all = {
    'mysql':['mysql-connector-python>=1.2.2'],
    'mongodb': ['pymongo>=3.2.1'],
    'testing': [
    'mock>=2.0.0',
    'pbr>=1.10.0',
    'funcsigs>=1.0.2'
    ]
}

setup(
    name='ssguan',
    version=ssguan.__version__,

    description='A Powerful Content Crawling Analytics Management Engine',
    long_description=long_description,

    url='www.suishouguan.com',

    author='Samuel Bai',
    author_email='samuelbaizg@gmail.com',

    license='Private License, Version 1.0',

    classifiers=[
        'Development Status :: 0.5',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',

        'License :: OSI Approved :: Apache Software License',

        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',

        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='scrapy crawler analytics',

    packages=find_packages(exclude=['data', 'tests*']),

    install_requires=install_requires,

    extras_require={
        'all': extras_require_all,
        'test': [
            'coverage',
        ]
    },

    package_data={
        'ssguan': [                        
            'config/*',
            'versions/*'       
        ],
    },

    entry_points={
        'console_scripts': [
            'ssguan=ssguan.run:main'
        ]
    },

    test_suite='tests.all_suite',
)