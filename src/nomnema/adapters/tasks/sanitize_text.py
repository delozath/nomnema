import re
from typing import Optional, override
from dataclasses import dataclass, field

import unicodedata as ud
from dataclasses import dataclass

from nomnema.domain.const import (
    UNICODE_REPLACEMENTS,
    DEFAULT_PUNCTUATION,
    BIBLATEX_ESCAPE,
    BIBLATEX_VERBATIM_FIELDS
)


@dataclass(frozen=True, slots=True)
class EntryTextSanitizer:
    normalization: str = "NFC"
    replacements: tuple[tuple[str, str], ...] = UNICODE_REPLACEMENTS
    punctuation: frozenset[str] = DEFAULT_PUNCTUATION

    def __call__(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError(
                f"Expected str, got {type(text).__name__}"
            )

        text = self._canonicalize(text)

        output: list[str] = []
        pending_space = False

        for char in text:
            if self._is_allowed(char):
                if pending_space and output:
                    output.append(" ")

                output.append(char)
                pending_space = False

            elif char.isspace():
                pending_space = bool(output)

        return "".join(output)

    def _canonicalize(self, text: str) -> str:
        text = ud.normalize(self.normalization, text)

        for source, target in self.replacements:
            text = text.replace(source, target)

        return text

    def _is_allowed(self, char: str) -> bool:
        return (
            ud.category(char)[0] in {"L", "M", "N"}
            or char in self.punctuation
        )


@dataclass(frozen=True, slots=True)
class BibLaTeXEscaper:
    verbatim_fields: frozenset[str] = BIBLATEX_VERBATIM_FIELDS

    def __call__(self, text: str, *, field: str) -> str:
        if not isinstance(text, str):
            raise TypeError(
                f"Expected str, got {type(text).__name__}"
            )

        if not isinstance(field, str):
            raise TypeError(
                f"Expected field as str, got {type(field).__name__}"
            )

        if field.casefold() in self.verbatim_fields:
            return text

        return text.translate(BIBLATEX_ESCAPE)





class tmp:
    def clean_bibkey(self, bib_entry: dict) -> dict:
        """
        Sanitize BibLaTeX entry key by removing underscores and normalizing encoding.

        Parameters
        ----------
        bib_entry : dict
            BibLaTeX entry as a dictionary.

        Returns
        -------
        dict
            BibLaTeX entry with cleaned key in ASCII format.   
        """
        bib_entry['ID'] = (
                unicodedata.normalize(
                    'NFKD',
                    bib_entry['ID'].replace('_', '')
             ).encode('ascii', 'ignore').decode('ascii'))

        return bib_entry
    
    def clean_fields(self, bib_entry: dict) -> dict:
        """
        Clean BibLaTeX entry fields by normalizing encoding and replacing LaTeX special characters.

        Parameters
        ----------
        bib_entry : dict
            BibLaTeX entry as a dictionary.

        Returns
        -------
        dict
            BibLaTeX entry with cleaned fields. 
        """
        for k in [k for k in bib_entry.keys() if k not in ['ID', 'year']]:
            tmp = unicodedata.normalize('NFC', bib_entry[k])
            for old, new in self.latex_chars:
                tmp = tmp.replace(old, new).replace("4â€“", '-')
            bib_entry[k] = tmp
        
        return bib_entry
