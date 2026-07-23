import unicodedata

import pytest

from nomnema.adapters.tasks.sanitize_text import (
    GeneralTextSanitizer,
)


class TestCleanEncodingSpanishAccentuation:
    """NFD-decomposed accents are a frequent artifact of PDF copy/paste and
    AI-generated markdown; clean_encoding must recompose them (NFC) so
    Spanish names render with a single precomposed accented character."""

    @pytest.mark.parametrize(
        "name",
        [
            "José",
            "María",
            "Muñoz",
            "Peña",
            "Íñigo",
            "Núñez",
            "Ángel",
            "Óscar",
            "Ibáñez",
            "Ordóñez",
        ],
    )
    def test_recomposes_nfd_decomposed_name_to_nfc(self, name):
        result = GeneralTextSanitizer.clean_encoding(name)

        assert result == name
        assert unicodedata.is_normalized("NFC", result)

    def test_recomposes_mixed_sentence(self):
        text = "El paciente José Muñoz presentó síntomas."
        result = GeneralTextSanitizer.clean_encoding(text)

        assert result == "El paciente José Muñoz presentó síntomas."


class TestCleanEncodingCommonMojibake:
    """Encoding glitches that regularly show up in AI markdown output or
    text copied from PDFs: stray surrogate code points from lossy
    decoding steps upstream (e.g. errors='surrogateescape')."""

    def test_strips_lone_surrogate_from_broken_decode(self):
        text = "café\udc80 con leche"
        result = GeneralTextSanitizer.clean_encoding(text)

        assert result == "café con leche"
        assert "\udc80" not in result

    def test_strips_lone_high_surrogate(self):
        text = "resumen\ud83d roto"
        result = GeneralTextSanitizer.clean_encoding(text)

        assert result == "resumen roto"

    def test_strips_multiple_stray_surrogates(self):
        text = "\ud800inicio\udfffmedio\ud800fin"
        result = GeneralTextSanitizer.clean_encoding(text)

        assert result == "iniciomediofin"


class TestCleanEncodingPassthroughCharacters:
    """Characters that are valid Unicode (not encoding errors) must survive
    clean_encoding untouched, even though they commonly appear alongside
    real mojibake in AI/PDF text."""

    @pytest.mark.parametrize(
        "text",
        #TODO estos caractateres si os deberia eliminar el sanitizer, ajusta el codigo y el test
        [
            "resultados preliminares",  # non-breaking space
            "co­operación",  # soft hyphen
            "rango 10–20",  # en dash
            "cita — referencia",  # em dash
            "“texto entrecomillado”",  # curly quotes
            "series…",  # ellipsis
            "diﬁcultad",  # fi ligature
        ],
    )
    def test_valid_unicode_punctuation_is_preserved(self, text):
        result = GeneralTextSanitizer.clean_encoding(text)

        assert result == text


class TestCleanEncodingEdgeCases:
    def test_empty_string_returns_empty_string(self):
        assert GeneralTextSanitizer.clean_encoding("") == ""

    def test_plain_ascii_is_unchanged(self):
        text = "Standard ASCII abstract text."

        assert GeneralTextSanitizer.clean_encoding(text) == text

    def test_leading_byte_order_mark_is_preserved(self):
        text = "﻿Título del artículo"

        result = GeneralTextSanitizer.clean_encoding(text)

        assert result == text

    def test_return_type_is_str(self):
        result = GeneralTextSanitizer.clean_encoding("texto de prueba")

        assert isinstance(result, str)
