import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="CSV2RDF",
    version="0.0.1",
    author="Mikko Koho",
    author_email="mikko.koho@iki.fi",
    description="A tool for converting a CSV file to simple RDF",
    license="MIT",
    keywords="csv, rdf, linked data",
    url="",
    long_description=read('README.md'),
    packages=['CSV2RDF'],
)
