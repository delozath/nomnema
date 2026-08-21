import re
from dataclasses import dataclass

import unicodedata as ud
from dataclasses import dataclass

from nomnema.domain.const import (
    UNICODE_REPLACEMENTS,
    DEFAULT_PUNCTUATION,
    BIBLATEX_ESCAPE,
    BIBLATEX_VERBATIM_FIELDS,
    NAME_SPECIAL_LETTERS,
    BIBLATEX_SHORT_ESCAPE
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


class BibEntryShortNormalizer:
    def __call__(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError(
                f"Expected str, got {type(text).__name__}"
            )
        
        return text.translate(BIBLATEX_SHORT_ESCAPE)


@dataclass(frozen=True, slots=True)
class BibKeyNormalizer:
    separator: str = "-"

    def __call__(self, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"Expected str, got {type(value).__name__}"
            )

        key = self._to_ascii(value)
        key = re.sub(r"[^a-z0-9]+", self.separator, key)
        key = key.strip(self.separator)

        if not key:
            raise ValueError(
                "The value does not produce a valid BibLaTeX key"
            )

        return key[:1].upper() + key[1:]

    @staticmethod
    def _to_ascii(value: str) -> str:
        value = value.casefold().translate(NAME_SPECIAL_LETTERS)
        value = ud.normalize("NFKD", value)

        return "".join(
            char
            for char in value
            if char.isascii() and not ud.combining(char)
        )