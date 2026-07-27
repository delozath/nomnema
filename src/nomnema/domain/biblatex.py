import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import BibDatabase


import pandas as pd

class BiblatexDriver:
    def __init__(self, bib_path="temp"):
        self.parser = BibTexParser(common_strings=True, interpolate_strings=False)

        with open (bib_path, 'r', encoding='utf-8') as bib_file:
            self.bib_db = bibtexparser.load(bib_file, parser=self.parser)

        self.cache_unique_doi = pd.DataFrame(self.bib_db.entries)['doi'].to_list()
        self.bib_path = bib_path
    
    def entry2parser(self, bib_entry):
        parser = BibTexParser(interpolate_strings=False)
        bib_parsed = bibtexparser.loads(bib_entry, parser=parser) 
        return bib_parsed

    def append_abstract(self, bib_entry, abstract):
        bib_parsed = self.entry2parser(bib_entry)
        bib_parsed.entries[0]['abstract'] = abstract

        return bib_parsed.entries[0]

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