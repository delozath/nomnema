import pytest
import os
from dotenv import load_dotenv

from nomnema.adapters.tasks.extract_doi import (
  ExtractDOIfromMarkdown,
  FetchBibEntryfromDOI2Bibtex
)


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


class TestFetchBibEntryfromDOI2Bibtex:
    @pytest.mark.parametrize(
        ("test_doi", "title_extract"),
        [
          ("10.1016/j.cmpb.2024.108283", "An algorithm to detect"),
          ("10.1016/j.inffus.2025.103768", "Ultrasound image segmentation"),
          ("10.1016/j.shj.2026.100849", "Prognostic Utility of the Dicrotic Notch"),
          ("10.1371/journal.pone.0324285", "valuating the effectiveness of data governance frameworks"),
        ],
    )
    def test_fetch_bib_entry_from_doi(
        self, test_doi, title_extract
    ):

        result = FetchBibEntryfromDOI2Bibtex().perform(test_doi, timeout_s=10.0)
        assert title_extract in result
