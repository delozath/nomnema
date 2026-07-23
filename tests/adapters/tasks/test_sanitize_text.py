import unicodedata

import pytest

from nomnema.adapters.tasks.sanitize_text import (
    EntryTextSanitizer,
)


class TestNamesNoChangeWithinText:
    @pytest.mark.parametrize(
        "name",
        [
            "José",
            "María",
            "Muñoz",
            "Íñigo",
            "Núñez",
            "Müller",
            "Strauß",
            "Noël",
            "Caphè",
            "Østby",
            "Åsen",
            "Gonçalves",
            "Öç",
            "Næs",
            "Wałęsa", 
            "Kowalski",
            "Żurek",
            "Kowalńyk",
            "Háček",
            "Dvořák",
            "Lebrûn"
        ],
    )
    def test_different_native_characters(self, name):
        sanitize_text = EntryTextSanitizer()
        result = sanitize_text(name)
        assert name == result

    @pytest.mark.parametrize(
            "test_word",
            [
               "﻿Hola mundo",
               "co­operación simple",
               "Hola​mundo",
               "“Hola mundo”",
               "‘Hola mundo’",
               "Texto–con guion",
               "Texto—con guion",
               "Título del artículo",
               "ABC１２３",
               "ﬁnal simple",
               "Hola 😀 mundo",
               "Precio €100",
               "Temperatura 25°C",
               "Texto™ simple",
               "Hola    mundo",
               "Texto con espacio",
            ],
        )
    def test_different_not_valida_charactes(self, test_word):
        sanitize_text = EntryTextSanitizer()
        result = sanitize_text(test_word)
        #print(f'''\n\n"{test_word}", "{result}"''')
        breakpoint()
        assert True
    



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
