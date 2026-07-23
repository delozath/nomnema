import re
from typing import Optional, override

from nomnema.ports.core import BaseService

import unicodedata


class GeneralTextSanitizer(BaseService):
    latex_chars = (
        (r'\&amp', r'\&'),
        (r'~', ''),
        (r'‐', '-'),
        (r'–', '-'),
        (r'_', r'\_')
     )
    
    @override
    def run(self, text, *args, **kwargs):
        text = GeneralTextSanitizer.clean_encoding(text)
    
    @staticmethod
    def clean_encoding(text: str) -> str:
        """
        Normalize text encoding to NFC and remove non-UTF-8 characters.

        Parameters
        ----------
        text : str
            Input text to be cleaned.
        
        Returns
        -------
        str
            Cleaned text with normalized encoding.
        """
        text = (
            unicodedata
                .normalize('NFC', text)
                .encode('utf-8', 'ignore')
                .decode('utf-8')
         )
        return text

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
