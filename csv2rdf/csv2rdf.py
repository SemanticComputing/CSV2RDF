#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Generic lightweight CSV to RDF converter.
"""

import argparse

from rdflib import URIRef, util, Graph, RDF, Literal, Namespace
import pandas as pd
from slugify import slugify


class CSV2RDF:
    """
    CSV to RDF conversion class
    """

    def __init__(self):
        self.table = None
        self.data = None
        self.schema = None

    def read_csv(self, input_csv, **kwargs):
        """
        Read in a CSV files using pandas.read_csv

        :param input_csv: CSV input (filename or buffer)
        :param kwargs: keyword arguments for pd.read_csv
        :return:
        """
        self.table = pd.read_csv(input_csv, **kwargs)

        self.table = self.table.fillna('').applymap(lambda x: x.strip() if type(x) == str else x)

    def convert_to_rdf(self, data_ns, schema_ns, instance_class):
        """
        Convert CSV to RDF. Each row of CSV is treated as one entity of a given class.
        CSV columns represent property values. Separate RDF graphs are created for instance data and schema.

        :param data_ns: Namespace for resource URIs
        :param schema_ns: Namespace for property URIs
        :param instance_class: RDF Class to use for created instances.
        :return:
        """
        self.data = Graph()
        self.schema = Graph()

        column_headers = list(self.table)

        for index in range(len(self.table)):
            for column in range(len(column_headers)):

                # TODO: Error handling for unknown columns
                column_name = column_headers[column]
                resource_uri = data_ns['r_' + str(index)]

                property_uri = schema_ns[slugify(column_name)]

                self.data.add((resource_uri, RDF.type, instance_class))
                self.schema.add((property_uri, RDF.type, RDF.Property))

                value = self.table.ix[index][column]

                if value:
                    self.data.add((resource_uri, property_uri, Literal(value)))

    def write_rdf(self, output_file_data, output_file_schema, fformat='turtle'):
        """
        Serialize graphs
        """
        if output_file_data:
            self.data.serialize(format=fformat, destination=output_file_data)
        if output_file_schema:
            self.schema.serialize(format=fformat, destination=output_file_schema)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--outdata", help="Output RDF data file", default="output_data.ttl")
    parser.add_argument("--outschema", help="Output RDF schema file", default="output_schema.ttl")
    parser.add_argument("--tclass", metavar="TARGET_CLASS", help="Target class for target property values",
                        default="http://example.org/Class")
    parser.add_argument("--tnamespace", metavar="TARGET_NAMESPACE", help="Namespace for target values", default="http://")
    parser.add_argument("--schemanamespace", metavar="SCHEMA_NAMESPACE", help="Namespace for property URIs",
                        default="http://")

    parser.add_argument("--format", default='guess', type=str,
                        help="Output format of RDF file [default: guess format from filename]")

    parser.add_argument("--quotechar",
                        help="CSV file quote character. The character used to denote the start and end of a quoted "
                             "item. Quoted items can include the delimiter and it will be ignored.")
    parser.add_argument("--sep",
                        help="CSV file delimiter to use. If sep is None, will try to automatically determine this. "
                             "Separators longer than 1 character and different from ‘s+’ will be interpreted as "
                             "regular expressions, will force use of the python parsing engine and will ignore quotes "
                             "in the data. Regex example: ‘rt’")
    parser.add_argument("--encoding", help="CSV file encoding to use for UTF when reading/writing (ex. ‘utf-8’).")
    parser.add_argument("--na_values",
                        help="CSV file Additional strings to recognize as NA/NaN. If dict passed, specific per-column "
                             "NA values.")

    args = parser.parse_args()

    DATA_NAMESPACE = Namespace(args.tnamespace)
    SCHEMA_NAMESPACE = Namespace(args.schemanamespace)

    INSTANCE_CLASS = URIRef(args.tclass)

    OUTPUT_FORMAT = util.guess_format(args.outdata) if args.format == 'guess' else args.format

    #################################

    converter = CSV2RDF()

    read_csv_kwargs = dict()
    if args.quotechar is not None:
        read_csv_kwargs.update({'quotechar': args.quotechar})
    if args.sep is not None:
        read_csv_kwargs.update({'sep': args.sep})
    if args.encoding is not None:
        read_csv_kwargs.update({'encoding': args.encoding})
    if args.na_values is not None:
        read_csv_kwargs.update({'na_values': eval(args.na_values)})  # Eval to allow lists

    # Read CSV

    converter.read_csv(args.input, **read_csv_kwargs)

    # Convert to RDF

    converter.convert_to_rdf(DATA_NAMESPACE, SCHEMA_NAMESPACE, INSTANCE_CLASS)
    converter.write_rdf(args.outdata, args.outschema, fformat=OUTPUT_FORMAT)
