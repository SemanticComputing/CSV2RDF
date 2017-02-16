#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Minimal tests for data conversion
"""
import io
import unittest

from rdflib import Namespace
from rdflib import URIRef

from csv2rdf import CSV2RDF


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

        assert len(list(converter.data)) == 12  # 2 instances + 10 properties
