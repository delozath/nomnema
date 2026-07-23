import re

_DOI_RE = re.compile(
    r"(?:https?://(?:dx\.)?doi\.org/)?(?P<doi>10\.\d{4,9}/[-._;()/:A-Z0-9]+)",
    re.IGNORECASE,
)
_DOI_PREFIX_RE = re.compile(
    r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)",
    re.IGNORECASE,
)


class DOIError(ValueError):
    """Base exception for DOI-related validation errors."""


class InvalidDOIFormatError(DOIError):
    def __init__(self, doi: str, reason: str) -> None:
        self.doi = doi
        self.reason = reason
        super().__init__(f"Invalid DOI format {doi!r}: {reason}")


def normalize_doi(value: str) -> str:
    doi = _DOI_PREFIX_RE.sub("", value.strip(), count=1).strip()
    if _DOI_RE.fullmatch(doi) is None:
        raise InvalidDOIFormatError(value, "expected a DOI such as 10.1000/example")
    return doi

def extract_doi(content: str) -> str:
    match = _DOI_RE.search(content)
    if match is None:
        return ""
    return match.group("doi").rstrip(".,;:)")
