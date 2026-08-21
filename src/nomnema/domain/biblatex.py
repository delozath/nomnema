import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import BibDatabase


import pandas as pd

class BiblatexDriver:
    def __init__(self, bib_path="temp"):
        self.parser = BibTexParser(common_strings=True, interpolate_strings=False)

        with open (bib_path, 'r', encoding='utf-8') as bib_file:
            self.bib_db = bibtexparser.load(bib_file, parser=self.parser)
        
        if self.bib_db.entries:
            self.cache_unique_doi = pd.DataFrame(self.bib_db.entries)['doi'].to_list()
        else:
            self.cache_unique_doi = []  
        self.bib_path = bib_path
    
    def add_entry(self, entry):
        self.bib_db.entries.append(entry)
        self.cache_unique_doi.append(entry['doi'])

    def dict_to_bibtex(self, entry: dict[str, str]) -> str:
        database = BibDatabase()
        database.entries = [entry]

        return bibtexparser.dumps(database).strip()

    def save(self):
        with open(self.bib_path, 'w') as writer:
            bibtexparser.dump(self.bib_db, writer)


class BibEntryParser:
    def __init__(self):
        self.parser = BibTexParser(interpolate_strings=False)
    
    def __call__(self, bib_entry: str) -> dict:
        if not isinstance(bib_entry, str):
            raise TypeError(f"bib_entry must be str, `{type(bib_entry)}` type was passed")
        bib_parsed = bibtexparser.loads(bib_entry, parser=self.parser) 
        return bib_parsed.entries[0]
