#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
'''
Create an RDF vocabulary from literal RDF values
'''
import argparse

import logging

import sys
from rdflib import *
from rdflib.namespace import SKOS
from slugify import slugify

logging.basicConfig(filename='vocab.log', filemode='a', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)


def create_unused_uri(uri, used_uris, value):
    orig_uri = uri
    i = 1
    while uri in used_uris:
        log.info('Changing duplicate URI: %s <--> %s' % (used_uris[uri], orig_uri))
        uri = "{uri}_{index}".format(uri=uri, index=i)
        i += 1

    return URIRef(uri)


def vocabularize(graph, namespace, property, target_property, target_class, literal_lang='fi'):
    """
    Transform literal values into a RDF flat RDF vocabulary. Splits values by '/'.

    :return:
    """

    output = Graph()
    vocab = Graph()
    used_uris = {}

    log.debug('Starting vocabulary creation')

    for (sub, obj) in graph.subject_objects(property):
        for value in [occ.strip().lower() for occ in str(obj).split('/')]:

            new_obj = namespace[slugify(value)]
            print("%s  -  %s" % (new_obj, type(new_obj)))
            if used_uris.get(new_obj) == value:
                new_obj = create_unused_uri(new_obj, used_uris, value)

            used_uris.update({new_obj: value})

            output.add((sub, target_property, new_obj))
            vocab.add((new_obj, RDF.type, target_class))
            vocab.add((new_obj, SKOS.prefLabel, Literal(value, lang=literal_lang)))

    log.debug('Vocabulary creation finished')
    return output, vocab


def main(args):
    """
    Main function for running via the command line.

    `args` is the list of command line arguments.
    """
    argparser = argparse.ArgumentParser(description="Create flat ontology based on input file and property",
                                        fromfile_prefix_chars='@')

    argparser.add_argument("input", help="Input RDF data file")
    argparser.add_argument("output", help="Output RDF data file")
    argparser.add_argument("output_vocab", help="Output RDF vocabulary file")
    argparser.add_argument("property", metavar="SOURCE_PROPERTY", help="Property used in input file")
    argparser.add_argument("tproperty", metavar="TARGET_PROPERTY", help="Target property for output file")
    argparser.add_argument("tclass", metavar="TARGET_CLASS", help="Target class for target property values")
    argparser.add_argument("tnamespace", metavar="TARGET_NAMESPACE", help="Namespace for target values")

    argparser.add_argument("--remove", dest='remove', action='store_true', default=False,
                           help="Remove original property triples")

    argparser.add_argument("--format", default='turtle', type=str, help="Format of RDF files [default: turtle]")

    argparser.add_argument("--mapping", metavar='FILE', type=str,
                           help="File containing value mappings (Not implemented)")

    args = argparser.parse_args()

    ns_target = Namespace(args.tnamespace)
    input_graph = Graph().parse(args.input, format=args.format)

    log.debug('Parsed input file')

    annotations, vocabulary = vocabularize(input_graph, Namespace(ns_target), URIRef(args.property),
                                           URIRef(args.tproperty), URIRef(args.tclass))

    annotations.serialize(format=args.format, destination=args.output)
    vocabulary.serialize(format=args.format, destination=args.output_schema)

    log.debug('Serialized output files')


if __name__ == '__main__':
    main(sys.argv)
