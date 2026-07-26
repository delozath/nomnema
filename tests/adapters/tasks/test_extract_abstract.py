import pytest
import os
from dotenv import load_dotenv

import time

from nomnema.adapters.tasks.extract_abstract import (
    FetchAbstractFromPubMedDOI,
    FetchAbstractFromCrossrefDOI,
    FetchAbstractChain
)

# NOTE: to migrate to Marker-based abstract extractor from PDF
"""
class TestExtractDOIfromMarkdown:
    @pytest.mark.parametrize(
        ("environment_variable", "expected_doi"),
        [
            ("PDF_FILE_TEST_1", "10.1016/j.cmpb.2024.108283"),
            ("PDF_FILE_TEST_2", "10.1016/j.inffus.2025.103768"),
            ("PDF_FILE_TEST_3", "10.1016/j.shj.2026.100849"),
            ("PDF_FILE_TEST_4", "10.1371/journal.pone.0324285"),
        ],
    )
    def test_extract_doi_returns_doi_from_plain_text(
        self, environment_variable, expected_doi
    ):
        load_dotenv()
        test_file = os.getenv(environment_variable)
        result = ExtractDOIfromMarkdown.perform(test_file)

        assert result == expected_doi
"""

import json
class TestFetchAbstractFromPubMedDOI:
    @pytest.mark.parametrize(
        ("test_doi", "abstract_extract"),
        [
          ("10.1016/j.cmpb.2024.108283", "BACKGROUND AND OBJECTIVE: Detection of the dicrotic notch (DN)"),
          ("10.1016/j.shj.2026.100849", "BACKGROUND: The dicrotic notch (DN) on the central aortic pressure"),
          ("10.1371/journal.pone.0324285", "Blockchain technology is widely used in almost every domain of life nowadays"),
        ],
    )
    def test_fetch_abstract_well_defined(
        self, test_doi, abstract_extract
    ):
        connection = FetchAbstractFromPubMedDOI()
        result = connection.fetch(content=test_doi, email="omar@mail.net")
        assert abstract_extract in result
        time.sleep(2) #needed to avoid saturate the PubMed public API

    @pytest.mark.parametrize(
            ('test_doi'),
            [
                "10.1016/j.inffus.2025.103768",
                "10.1016/fake"
            ]
    )
    def test_fetch_abstract_not_in_pubmed_or_wrong_doi(self, test_doi):
        connection = FetchAbstractFromPubMedDOI()
        result = connection.fetch(content=test_doi, email="omar@mail.net")
        assert result is None
        time.sleep(2)


class TestFetchAbstractFromCrossrefDOI:
    @pytest.mark.parametrize(
            ("test_doi", "abstract_extract"),
            [
                ("10.1029/2019GL084053", "Abstract New broadband seismic data from Botswana and"),
                ("10.3102/0162373709352369", "Research in fields other than education has found"),
                ("10.1002/anie.202006283", "Abstract Main group analogues of cyclobutane"),
            ]
    )
    def test_fetch_abstract_well_defined(self, test_doi, abstract_extract):
        connection = FetchAbstractFromCrossrefDOI()
        result = connection.fetch(content=test_doi, email="omar@mail.net", clean=True)
        assert abstract_extract in result
        time.sleep(2)
    
    def test_fetch_abstract_not_in_crossref(self):
        test_doi = "10.1016/j.inffus.2025.103768"
        connection = FetchAbstractFromCrossrefDOI()
        result = connection.fetch(content=test_doi, email="omar@mail.net", clean=True)
        assert result is None
        time.sleep(5)

    def test_fetch_abstract_wrong_doi(self):
        test_doi = "10.1016/fake"
        connection = FetchAbstractFromCrossrefDOI()

        with pytest.raises(RuntimeError):
            connection.fetch(content=test_doi, email="omar@mail.net", clean=True)


class TestFetchAbstractChain:
    @pytest.mark.parametrize(
        ("test_doi", "fetcher", "params"),
        [
          ("10.1016/j.cmpb.2024.108283", "fetch abstract from PubMed DOI", {}),
          ("10.1371/journal.pone.0324285", "fetch abstract from PubMed DOI", {'clean': True}),
          ("10.3102/0162373709352369", "fetch abstract from Crossref DOI", {'clean': True}),
          ("10.1002/anie.202006283", "fetch abstract from PubMed DOI", {}), # is in PubMed also
        ],
    )
    def test_correct_doi_standard_format(self, test_doi, fetcher, params):
        chain = FetchAbstractChain(test_doi, 'omar@mail.net')
        _, identifier = chain.run(**params) # abstract fetch tested above
        assert fetcher == identifier
        time.sleep(4)

    @pytest.mark.parametrize(
        ("test_doi", "fetcher", "params"),
        [
          ("https://dx.doi.org/10.1016/j.cmpb.2024.108283", "fetch abstract from PubMed DOI", {}),
          ("https://dx.doi.org/10.1371/journal.pone.0324285", "fetch abstract from PubMed DOI", {'clear': True}),
          ("https://dx.doi.org/10.3102/0162373709352369", "fetch abstract from Crossref DOI", {'clear': True}),
          ("https://dx.doi.org/10.1002/anie.202006283", "fetch abstract from PubMed DOI", {}), # is in PubMed also
        ],
    )
    def test_correct_doi_within_dx_doi(self, test_doi, fetcher, params):
        chain = FetchAbstractChain(test_doi, 'omar@mail.net')
        _, identifier = chain.run(**params) # abstract fetch tested above
        assert fetcher == identifier
        time.sleep(4)

    @pytest.mark.parametrize(
        ("test_doi"),
        [
          "https://dx.doi.org/10.1016/j.cmpb.2024.108283/fake",
          "https://dx.doi.org/10.1016/j.fake.2024.108283",
          "10.1016/j.fake.2024.108283",
        ],
    )
    def test_correct_doi_errors(self, test_doi):
        chain = FetchAbstractChain(test_doi, 'omar@mail.net')
        with pytest.raises(RuntimeError):
            _, _ = chain.run()
            time.sleep(4)
    