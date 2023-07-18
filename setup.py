#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from glob import glob
from os import path
from os.path import join as pjoin


from setupbase import (
    create_cmdclass, install_npm, ensure_targets,
    find_packages, combine_commands,
    get_version, HERE
)

from setuptools import setup


# The name of the project
name = 'powerbiclient'

# Get our version
version = get_version(pjoin(name, '_version.py'))

# Get Readme file content
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

nb_path = pjoin(HERE, name, 'nbextension', 'static')
lab_path = pjoin(HERE, name, 'labextension')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(nb_path, 'index.js'),
    pjoin(HERE, 'lib', 'plugin.js'),
]

package_data_spec = {
    name: [
        'nbextension/static/*.*js*',
        'labextension/*.tgz'
    ]
}

data_files_spec = [
    ('share/jupyter/nbextensions/powerbiclient',
        nb_path, '*.js*'),
    ('share/jupyter/lab/extensions', lab_path, '*.tgz'),
    ('etc/jupyter/nbconfig/notebook.d', HERE, 'powerbiclient.json')
]


cmdclass = create_cmdclass('jsdeps', package_data_spec=package_data_spec,
                           data_files_spec=data_files_spec)
cmdclass['jsdeps'] = combine_commands(
    install_npm(HERE, build_cmd='build:all'),
    ensure_targets(jstargets),
)


setup_args = dict(
    name=name,
    description='A Custom Jupyter Widget Library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=version,
    scripts=glob(pjoin('scripts', '*')),
    cmdclass=cmdclass,
    packages=find_packages(),
    author='Microsoft',
    author_email='',
    url='https://github.com/Microsoft/powerbi-jupyter',
    license='MIT',
    platforms="Linux, Mac OS X, Windows",
    keywords=['Jupyter', 'Widgets', 'IPython'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Jupyter',
    ],
    include_package_data=True,
    install_requires=[
        'ipywidgets>=7.0.0',
        'jupyter-ui-poll>=0.1.2',
        'msal>=1.8.0',
        'requests>=2.25.1',
        'pandas',
        'pyspark'
    ],
    extras_require={
        'test': [
            'pytest>=4.6',
            'pytest-cov',
            'nbval',
            'requests_mock',
            'mock'
        ],
        'demo': [
            'pandas',
            'matplotlib',
        ],
    },
    entry_points={
    },
    python_requires='>=3.4'
)

if __name__ == '__main__':
    setup(**setup_args)
