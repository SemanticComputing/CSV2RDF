#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Tests for data conversion
"""
import io
import unittest

from rdflib import Namespace, Literal
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

    def test_create_unused_uri(self):
        uri = create_unused_uri('http://example.com/kahmija', {'http://example.com/kahmija': 'kähmijä'})
        self.assertEquals(uri, URIRef('http://example.com/kahmija_1'))

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

    def test_vocab_literals_2(self):
        converter = CSV2RDF()
        test_csv = self.TEST_CSV + "\n1, näkki, 3, 4, 5" + "\n1, nakki, 3, 4, 5"
        converter.read_csv(io.StringIO(test_csv), **{'sep': ','})
        converter.convert_to_rdf(Namespace("http://example.com/"),
                                 Namespace("http://example.com/"),
                                 URIRef("http://example.com/Class"))

        ns_vocab = Namespace('http://example.com/vocab/')
        annotations, vocabulary = vocabularize(converter.data, ns_vocab,
                                               URIRef("http://example.com/col2"), SKOS.related, SKOS.Concept)

        labels = {vocabulary.value(ns_vocab['nakki'], SKOS.prefLabel),
                  vocabulary.value(ns_vocab['nakki_1'], SKOS.prefLabel)}

        expected_labels = {Literal('nakki', lang='fi'), Literal('näkki', lang='fi')}

        self.assertEquals(labels, expected_labels)

        self.assertEquals(vocabulary[ns_vocab['nakki']:RDF.type:SKOS.Concept], True)
        self.assertEquals(vocabulary[ns_vocab['nakki_1']:RDF.type:SKOS.Concept], True)

        self.assertIn(annotations.value(URIRef("http://example.com/r_3"), SKOS.related), [ns_vocab['nakki'], ns_vocab['nakki_1']])

