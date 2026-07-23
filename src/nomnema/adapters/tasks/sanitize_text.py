import re
from typing import Optional, override
from dataclasses import dataclass, field

import string
import unicodedata as ud

from nomnema.ports.core import BaseService

import unicodedata

from __future__ import annotations

import string
import unicodedata as ud
from dataclasses import dataclass


FULLWIDTH_ASCII_REPLACEMENTS: tuple[tuple[str, str], ...] = tuple(
    (chr(code), chr(code - 0xFEE0))
    for code in range(0xFF01, 0xFF5F)
)


DEFAULT_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    # Invisible / formatting
    ("\uFEFF", ""),
    ("\u200B", ""),
    ("\u200C", ""),
    ("\u200D", ""),
    ("\u2060", ""),
    ("\u00AD", ""),

    ("\u200E", ""),
    ("\u200F", ""),
    ("\u202A", ""),
    ("\u202B", ""),
    ("\u202C", ""),
    ("\u202D", ""),
    ("\u202E", ""),
    ("\u2066", ""),
    ("\u2067", ""),
    ("\u2068", ""),
    ("\u2069", ""),

    ("\uFE0E", ""),
    ("\uFE0F", ""),

    # Double quotes
    ("“", '"'),
    ("”", '"'),
    ("„", '"'),
    ("‟", '"'),
    ("«", '"'),
    ("»", '"'),
    ("〝", '"'),
    ("〞", '"'),
    ("〟", '"'),
    ("「", '"'),
    ("」", '"'),
    ("『", '"'),
    ("』", '"'),

    # Single quotes / apostrophes
    ("‘", "'"),
    ("’", "'"),
    ("‚", "'"),
    ("‛", "'"),
    ("‹", "'"),
    ("›", "'"),
    ("ʼ", "'"),
    ("ʻ", "'"),

    # Dashes
    ("‐", "-"),
    ("-", "-"),
    ("‒", "-"),
    ("–", "-"),
    ("—", "-"),
    ("―", "-"),
    ("−", "-"),
    ("﹘", "-"),
    ("﹣", "-"),

    # Ellipsis
    ("…", "..."),
    ("‥", ".."),
    ("․", "."),

    # PDF ligatures
    ("ﬀ", "ff"),
    ("ﬁ", "fi"),
    ("ﬂ", "fl"),
    ("ﬃ", "ffi"),
    ("ﬄ", "ffl"),
    ("ﬅ", "ft"),
    ("ﬆ", "st"),

    # Bullets
    ("•", "-"),
    ("‣", "-"),
    ("⁃", "-"),
    ("◦", "-"),
    ("▪", "-"),
    ("▫", "-"),

    # Unicode spaces
    ("\u00A0", " "),
    ("\u2000", " "),
    ("\u2001", " "),
    ("\u2002", " "),
    ("\u2003", " "),
    ("\u2004", " "),
    ("\u2005", " "),
    ("\u2006", " "),
    ("\u2007", " "),
    ("\u2008", " "),
    ("\u2009", " "),
    ("\u200A", " "),
    ("\u202F", " "),
    ("\u205F", " "),
    ("\u3000", " "),

    # Literal HTML entities
    ("&amp;", "&"),
    ("&quot;", '"'),
    ("&apos;", "'"),
    ("&#39;", "'"),
    ("&#x27;", "'"),
    ("&lt;", "<"),
    ("&gt;", ">"),

    ("&nbsp;", " "),
    ("&#160;", " "),
    ("&#xA0;", " "),
    ("&#xa0;", " "),
    ("&ensp;", " "),
    ("&emsp;", " "),
    ("&thinsp;", " "),
    ("&shy;", ""),

    ("&ldquo;", '"'),
    ("&rdquo;", '"'),
    ("&bdquo;", '"'),
    ("&lsquo;", "'"),
    ("&rsquo;", "'"),
    ("&sbquo;", "'"),

    ("&ndash;", "-"),
    ("&mdash;", "-"),
    ("&hellip;", "..."),

    # Numeric HTML entities
    ("&#8216;", "'"),
    ("&#8217;", "'"),
    ("&#8220;", '"'),
    ("&#8221;", '"'),
    ("&#8211;", "-"),
    ("&#8212;", "-"),
    ("&#8230;", "..."),

    ("&#x2018;", "'"),
    ("&#x2019;", "'"),
    ("&#x201C;", '"'),
    ("&#x201D;", '"'),
    ("&#x2013;", "-"),
    ("&#x2014;", "-"),
    ("&#x2026;", "..."),

) + FULLWIDTH_ASCII_REPLACEMENTS


DEFAULT_PUNCTUATION = frozenset(
    string.punctuation + "¿¡€$°"
)


@dataclass(frozen=True, slots=True)
class EntryTextSanitizer:
    normalization: str = "NFC"
    replacements: tuple[tuple[str, str], ...] = DEFAULT_REPLACEMENTS
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
