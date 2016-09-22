#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Generic lightweight CSV to RDF converter.
"""

import argparse

from rdflib import URIRef, util, Graph, RDF, Literal, Namespace
import pandas as pd
from slugify import slugify

#################################

parser = argparse.ArgumentParser(description='CSV2RDF')

parser.add_argument("input", help="Input CSV file")
parser.add_argument("output", help="Output RDF file")
parser.add_argument("tclass", metavar="TARGET_CLASS", help="Target class for target property values")
parser.add_argument("tnamespace", metavar="TARGET_NAMESPACE", help="Namespace for target values", default="http://")
parser.add_argument("schemanamespace", metavar="SCHEMA_NAMESPACE", help="Namespace for property URIs",
                    default="http://")

parser.add_argument("--format", default='guess', type=str,
                    help="Output format of RDF file [default: guess format from filename]")

parser.add_argument("--quotechar",
                    help="CSV file quote character. The character used to denote the start and end of a quoted item. "
                         "Quoted items can include the delimiter and it will be ignored.")
parser.add_argument("--sep",
                    help="CSV file delimiter to use. If sep is None, will try to automatically determine this. "
                         "Separators longer than 1 character and different from ‘s+’ will be interpreted as regular "
                         "expressions, will force use of the python parsing engine and will ignore quotes in the data. "
                         "Regex example: ‘rt’")
parser.add_argument("--encoding", help="CSV file encoding to use for UTF when reading/writing (ex. ‘utf-8’).")
parser.add_argument("--na_values",
                    help="CSV file Additional strings to recognize as NA/NaN. If dict passed, specific per-column NA "
                         "values.")

args = parser.parse_args()

DATA_NAMESPACE = Namespace(args.tnamespace)
SCHEMA_NAMESPACE = Namespace(args.schemanamespace)

INSTANCE_CLASS = URIRef(args.tclass)

OUTPUT_FORMAT = util.guess_format(args.output) if args.format == 'guess' else args.format

#################################

# Read CSV

read_csv_kwargs = dict()
if args.quotechar is not None:
    read_csv_kwargs.update({'quotechar': args.quotechar})
if args.sep is not None:
    read_csv_kwargs.update({'sep': args.sep})
if args.encoding is not None:
    read_csv_kwargs.update({'encoding': args.encoding})
if args.na_values is not None:
    read_csv_kwargs.update({'na_values': eval(args.na_values)})  # Eval to allow lists

table = pd.read_csv(args.input, **read_csv_kwargs)

table = table.fillna('').applymap(lambda x: x.strip() if type(x) == str else x)

#################################

# Convert to RDF

data = Graph()

column_headers = list(table)

for index in range(len(table)):
    for column in range(len(column_headers)):

        column_name = column_headers[column]
        resource_uri = DATA_NAMESPACE['r_' + str(index)]

        property_uri = SCHEMA_NAMESPACE[slugify(column_name)]

        data.add((resource_uri, RDF.type, INSTANCE_CLASS))

        value = table.ix[index][column]

        if value:
            data.add((resource_uri, property_uri, Literal(value)))

data.serialize(format=OUTPUT_FORMAT, destination=args.output)
