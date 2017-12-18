#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Tests for data conversion
"""
import io
import unittest

from rdflib import Namespace
from rdflib import URIRef
from rdflib.namespace import SKOS, RDF

from csv2rdf import CSV2RDF
from csv2rdf.vocab_literals import vocabularize, create_unused_uri


class TestCSV2RDF(unittest.TestCase):
    TEST_CSV = """COL1, COL2, COL3, COL4, COL5
1, 2, 3, 4, 5
6,7,8,9,10"""

    def test_conversion(self):
        converter = CSV2RDF()

        # Read CSV

        converter.read_csv(io.StringIO(self.TEST_CSV), **{'sep': ','})

        # Convert to RDF

        converter.convert_to_rdf(Namespace("http://example.com/"),
                                 Namespace("http://example.com/"),
                                 URIRef("http://example.com/Class"))

        self.assertEquals(len(list(converter.data)), 12)  # 2 instances + 10 properties

    def test_vocab_literals(self):
        converter = CSV2RDF()
        converter.read_csv(io.StringIO(self.TEST_CSV), **{'sep': ','})
        converter.convert_to_rdf(Namespace("http://example.com/"),
                                 Namespace("http://example.com/"),
                                 URIRef("http://example.com/Class"))

        ns_vocab = Namespace('http://example.com/vocab/')
        annotations, vocabulary = vocabularize(converter.data, ns_vocab,
                                               URIRef("http://example.com/col2"), SKOS.related, SKOS.Concept)

        self.assertEquals(len(annotations), 2)

        self.assertEquals(vocabulary[ns_vocab['2']:RDF.type:SKOS.Concept], True)
        self.assertEquals(vocabulary[ns_vocab['7']:RDF.type:SKOS.Concept], True)

    def test_create_unused_uri(self):
        uri = create_unused_uri('http://example.com/kahmija', {'http://example.com/kahmija': 'kähmijä'}, 'kahmija')
        self.assertEquals(uri, URIRef('http://example.com/kahmija_1'))
