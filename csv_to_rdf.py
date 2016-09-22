#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Generic lightweight CSV to RDF converter.
"""

import argparse

from rdflib import *
import pandas as pd
from slugify import slugify

#################################

parser = argparse.ArgumentParser(description='CSV2RDF')

parser.add_argument('-reload', action='store_true', help='Reload RDF graphs, instead of using pickle object')
args = parser.parse_args()
reload = args.reload

# TODO: Parse variables from arguments

DATA_NAMESPACE = 'http://ldf.fi/warsa/prisoners/'
SCHEMA_NAMESPACE = 'http://ldf.fi/schema/warsa/prisoners/'

INSTANCE_CLASS = URIRef(SCHEMA_NAMESPACE + 'PrisonerOfWar')

INPUT_FILE = 'test.csv'
OUTPUT_FILE = 'test.ttl'

#################################

table = pd.read_csv(INPUT_FILE, encoding='UTF-8', index_col=False, sep='\t', quotechar='"',
                    na_values=[' '])

table = table.fillna('').applymap(lambda x: x.strip() if type(x) == str else x)

data = Graph()

column_headers = list(table)

for index in range(len(table)):
    for column in range(len(column_headers)):

        column_name = column_headers[column]
        resource_uri = URIRef(DATA_NAMESPACE + 'r_' + str(index))

        property_uri = URIRef(DATA_NAMESPACE + slugify(column_name))

        data.add((resource_uri, RDF.type, INSTANCE_CLASS))

        value = table.ix[index][column]

        if value:
            data.add((resource_uri, property_uri, Literal(value)))

data.serialize(format="turtle", destination=OUTPUT_FILE)
