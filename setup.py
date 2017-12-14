import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="csv2rdf",
    version="0.1.3",
    author="Mikko Koho",
    author_email="mikko.koho@iki.fi",
    description="A tool for converting a CSV file to simple RDF",
    license="MIT",
    keywords="csv, rdf, linked data",
    url="",
    long_description=read('README.md'),
    packages=['csv2rdf'],
)
