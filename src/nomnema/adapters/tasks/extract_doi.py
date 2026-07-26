
from markitdown import MarkItDown

import requests

from nomnema.ports.core import BaseExtract
from nomnema.domain.validation import doi as doi_validation
from nomnema.domain.loader import LoaderPDFFile


class ExtractDOIfromMarkdown(BaseExtract[str, str]):
    @classmethod
    def perform(cls, content: str, *args, max_chars=6000, **kwargs) -> str:
        loader = LoaderPDFFile(str(content)) # here content is path to the PDF file
        decoded = loader.load(MarkItDown)
        first_page = decoded.markdown[:max_chars]
        doi_base = doi_validation.extract_doi(first_page)
        return doi_base


class FetchBibEntryfromDOI2Bibtex(BaseExtract[str, str]):
    def perform(self, content: str, *args, timeout_s: float = 10.0, **kwargs) -> str:
        """
        Fetch BibTeX entry from DOI using doi.org service.

        Parameters
        ----------
        content : str
            Digital Object Identifier.
        timeout_s : float, optional
            Request timeout in seconds. Default is 10.0 seconds.

        Returns
        -------
        str
            BibTeX entry as a string.
        """
        url = f"https://doi.org/{content.strip()}"
        headers = {
            "Accept": "application/x-bibtex",
            "User-Agent": "doi2bibtex/1.0 (mailto:you@example.com)",
        }
        try:
            res = requests.get(url, headers=headers, allow_redirects=True, timeout=timeout_s)
            res.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Status code: {res.status_code}")
            return ""

        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
            return ""

        except requests.exceptions.RequestException as err:
            print(f"An absolute wildcard error occurred: {err}")
            return ""
        
        else:
            return res.text.strip()
