import unicodedata

import pytest

from nomnema.adapters.tasks.sanitize_text import (
    EntryTextSanitizer,
    BibLaTeXEscaper
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
            ("test_word", "expected"),
            [
               ("﻿Hola mundo", "Hola mundo" ),
               ("co­operación simple", "cooperación simple"),
               ("Hola​mundo", "Holamundo"),
               ("“Hola mundo”", '"Hola mundo"'),
               ("‘Hola mundo’", "'Hola mundo'"),
               ("Texto–con guion", "Texto-con guion"),
               ("Texto—con guion", "Texto-con guion"),
               ("Título del artículo", "Título del artículo"),
               ("ABC１２３", "ABC123"),
               ("ﬁnal simple", "final simple"),
               ("Hola 😀 mundo", "Hola mundo"),
               ("Precio €100", "Precio €100"),
               ("Precio $100", "Precio $100"),
               ("Temperatura 25°C", "Temperatura 25°C"),
               ("Texto™ simple", "Texto™ simple"),
               ("Hola    mundo", "Hola mundo"),
               ("Texto con espacio", "Texto con espacio"),
            ],
        )
    def test_different_not_valida_charactes(self, test_word, expected):
        sanitize_text = EntryTextSanitizer()
        result = sanitize_text(test_word)
        assert result == expected
    


class TestBibLaTeXEscaper:
    @pytest.mark.parametrize(
        ("test_word", "expected", "field_type"),
        [
            (
                r"Ruta C:\docs\paper.pdf",
                r"Ruta C:\docs\paper.pdf",
                'url'
            ),
            (
                r"Ruta C:\docs\paper.pdf",
                r"Ruta C:\textbackslash{}docs\textbackslash{}paper.pdf",
                'abstract'
            ),
            (
                "Tom & Ana",
                r"Tom \& Ana",
                'author'
            ),
            (
                "Precisión del 95%",
                r"Precisión del 95\%",
                'abstract'
            ),
            (
                "Precisión del 95%",
                r"Precisión del 95\%",
                'title'
            ),
            (
                "Costo: $100",
                r"Costo: \$100",
                'abstract'
            ),
            (
                "Modelo #1",
                r"Modelo \#1",
                'title'
            ),
            (
                "FAUSP_NET",
                r"FAUSP\_NET",
                'abstract'
            ),
            (
                "Conjunto {A}",
                r"Conjunto \{A\}",
                'title'
            ),
            (
                "Usuario ~ admin",
                r"Usuario \textasciitilde{} admin",
                'note'
            ),
            (
                "Valor x^2",
                r"Valor x\textasciicircum{}2",
                'title'
            ),
        ]
    )
    def test_cases_latex_escaper(self, text_word, expected, field_type):
        latex_esc = BibLaTeXEscaper()
        result = latex_esc(text_word, field=field_type)
        assert result == expected