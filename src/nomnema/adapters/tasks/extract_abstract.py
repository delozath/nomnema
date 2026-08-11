import re
from typing import Optional, override

import requests
import xml.etree.ElementTree as ET

from nomnema.ports.core import BaseService, BaseExtractRemote
from nomnema.domain.validation.doi import normalize_doi
from nomnema.domain.validation import email


class FetchAbstractChain(BaseService):
    def __init__(self, doi, mailto):
        self.doi = normalize_doi(doi)
        self.email = email.raise_valid_email(mailto)
        self.chain = [
            FetchAbstractFromPubMedDOI,
            FetchAbstractFromCrossrefDOI
            #TODO add window to edit or add if not found
            #TODO add Marker decoder
        ]
    
    @override
    def run(self, /, **kwargs):
        clean = kwargs.get('clear', False)
        for cls in self.chain:
            abstrac = cls().fetch(self.doi, self.email, clean=clean)
            if abstrac:
                return abstrac, cls.__id__
        return None, "Abstract not found"


class BaseURLRequest(BaseExtractRemote[str, Optional[str]]):
    def request(self, url, params, message='Error connection', timeout=20):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(message) from e
        
        else:
            return response

    
class FetchAbstractFromPubMedDOI(BaseURLRequest):
    __id__ = "fetch abstract from PubMed DOI"
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    @override
    def fetch(self, content, email, **kwargs): # here content is the doi
        pmid = self._search_pmid_from_doi(content, email)
        if pmid is None:
            return
        else:
            abstract = self._fetch_abstract_from_pubmed(pmid, email)
            if abstract is None:
                return 
            else:
                return abstract

    def _search_pmid_from_doi(self, doi, email):
        search_url = f"{FetchAbstractFromPubMedDOI.BASE_URL}esearch.fcgi"

        search_params = {
            "db": "pubmed",
            "term": f'"{doi}"[AID]',
            "retmode": "json",
            "email": email,
            "tool": "AbstractFetcher",
        }

        search_response = self.request(
            search_url,
            search_params,
            message="Network or API Error in get PMID"
        )

        search_data = search_response.json()
        id_list = search_data.get(
            "esearchresult", {}
        ).get(
            "idlist", []
        )
        if not id_list:
            print(f"No PubMed record found for DOI: {doi}")
            return None
        
        pmid = id_list[0]
        print(f"Found PMID: {pmid}")
        return pmid
    
    def _fetch_abstract_from_pubmed(self, pmid, email):
        fetch_url = f"{FetchAbstractFromPubMedDOI.BASE_URL}efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "email": email,
            "tool": "AbstractFetcher",
        }

        fetch_response = self.request(
            fetch_url,
            params=fetch_params,
            message="Network or API Error in get abstract"
        )
        
        try:
            root = ET.fromstring(fetch_response.content)
            abstract_nodes = root.findall(".//AbstractText")
        
        except ET.ParseError as e:
            raise RuntimeError(f"XML get from PubMed Parsing Error") from e
            
        else:
            if not abstract_nodes:
                return
            return "\n\n" + self._compose_abstract(abstract_nodes)
    
    def _compose_abstract(self, nodes):
        abstract_parts = []

        for node in nodes:
            label = node.get("Label")
            text = "".join(node.itertext()).strip()

            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)
        
        return "".join(abstract_parts)


class FetchAbstractFromCrossrefDOI(BaseURLRequest):
    __id__ = "fetch abstract from Crossref DOI"

    BASE_URL = "https://api.crossref.org/works"

    @override
    def fetch(self, content: str, email: str, *args, clean=False, **kwargs) -> str | None:
        url = f"{FetchAbstractFromCrossrefDOI.BASE_URL}/{content}"
        params = {
            "mailto": email
        }
        
        response = self.request(
            url,
            params,
            message="Error connetion to Crossref request"
        )
        
        data = response.json()
        record = data.get("message", {})

        abstract = record.get("abstract")
        if not abstract:
            return

        if clean:
            return self._clean_text(abstract)
        
        return abstract
    
    def _clean_text(self, text):
        text = re.sub(
            r"<[^>]+>",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )
        return text.strip()