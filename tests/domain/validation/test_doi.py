import pytest

from nomnema.domain.validation.doi import (
    InvalidDOIFormatError,
    extract_doi,
    normalize_doi,
)


class TestNormalizeDOI:
    @pytest.mark.parametrize(
        ("doi"),
        [
            "10.1016/j.cmpb.2024.108283",
            "10.1016/j.inffus.2025.103768",
            "10.1016/j.shj.2026.100849",
            "10.1371/journal.pone.0324285",
        ],
    )
    def test_normalize_doi_plain_format_returns_same_doi(self, doi):
        result = normalize_doi(doi)

        assert result == doi

    @pytest.mark.parametrize(
        ("raw_value", "expected_doi"),
        [
            ("https://doi.org/10.1029/2019GL084053", "10.1029/2019GL084053"),
            ("https://dx.doi.org/10.3102/0162373709352369", "10.3102/0162373709352369"),
            ("doi:10.1002/anie.202006283", "10.1002/anie.202006283"),
            ("doi: 10.1016/j.cmpb.2024.108283", "10.1016/j.cmpb.2024.108283"),
        ],
    )
    def test_normalize_doi_strips_url_prefix(self, raw_value, expected_doi):
        result = normalize_doi(raw_value)

        assert result == expected_doi

    @pytest.mark.parametrize(
        ("invalid_value"),
        [
            "not-a-doi",
            "",
            "10.16/",
        ],
    )
    def test_normalize_doi_invalid_format_raises_error(self, invalid_value):
        with pytest.raises(InvalidDOIFormatError):
            normalize_doi(invalid_value)


class TestExtractDOI:
    @pytest.mark.parametrize(
        ("content", "expected_doi"),
        [
            (
                "The DOI is 10.1016/j.cmpb.2024.108283 for this reference.",
                "10.1016/j.cmpb.2024.108283",
            ),
            (
                "Available at https://dx.doi.org/10.1371/journal.pone.0324285 online.",
                "10.1371/journal.pone.0324285",
            ),
        ],
    )
    def test_extract_doi_from_surrounding_text(self, content, expected_doi):
        result = extract_doi(content)

        assert result == expected_doi

    @pytest.mark.parametrize(
        ("content", "expected_doi"),
        [
            ("The DOI is 10.1016/j.cmpb.2024.108283.", "10.1016/j.cmpb.2024.108283"),
            ("See (10.1016/j.shj.2026.100849);", "10.1016/j.shj.2026.100849"),
            ("Ref: 10.1371/journal.pone.0324285),", "10.1371/journal.pone.0324285"),
        ],
    )
    def test_extract_doi_strips_trailing_punctuation(self, content, expected_doi):
        result = extract_doi(content)

        assert result == expected_doi

    @pytest.mark.parametrize(
        ("content"),
        [
            "no identifier here",
            "",
        ],
    )
    def test_extract_doi_returns_empty_string_when_not_found(self, content):
        result = extract_doi(content)

        assert result == ""
