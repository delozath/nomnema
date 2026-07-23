import pytest
import os
from dotenv import load_dotenv

from nomnema.adapters.tasks.extract_doi import (
  ExtractDOIfromMarkdown,
  FetchBibEntryfromDOI2Bibtex
)


class TestExtractDOIfromMarkdown:
    @pytest.mark.parametrize(
        ("env_pfname", "env_doi"),
        [
            ("PDF_EXAMPLE_1", "DOI_EXAMPLE_1"),
            ("PDF_EXAMPLE_2", "DOI_EXAMPLE_2"),
            ("PDF_EXAMPLE_3", "DOI_EXAMPLE_3")
        ],
    )
    def test_extract_doi_returns_doi_from_plain_text(
        self, env_pfname, env_doi
    ):
        load_dotenv(".env-test")
        test_file = os.getenv(env_pfname)
        test_doi = os.getenv(env_doi)
        result = ExtractDOIfromMarkdown.perform(test_file)

        assert result == test_doi


class TestFetchBibEntryfromDOI2Bibtex:
    @pytest.mark.parametrize(
        ("fetch_doi", "title_extract"),
        [
          ("DOI_FETCH_1", "DOI_FETCH_EXTRACT_1"),
          ("DOI_FETCH_2", "DOI_FETCH_EXTRACT_2"),
          ("DOI_FETCH_3", "DOI_FETCH_EXTRACT_3"),
          ("DOI_FETCH_4", "DOI_FETCH_EXTRACT_4"),
        ],
    )
    def test_fetch_bib_entry_from_doi(
        self, fetch_doi, title_extract
    ):
        load_dotenv(".env-test")
        test_doi = os.getenv(fetch_doi)
        test_content = os.getenv(title_extract)

        result = FetchBibEntryfromDOI2Bibtex().perform(test_doi, timeout_s=10.0)
        assert test_content in result
