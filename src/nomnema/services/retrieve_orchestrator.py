from omegaconf import DictConfig

from shutil import move

from nomnema.ports.core import BaseService

from nomnema.storage.local_storage_validation import (
    LocalFileStorageValidation,
    LocalFolderStorageValidation,
)

from nomnema.adapters.tasks.extract_doi import (
  ExtractDOIfromMarkdown,
  FetchBibEntryfromDOI2Bibtex
)

from nomnema.adapters.tasks.extract_abstract import (
    #FetchAbstractFromPubMedDOI,
    #FetchAbstractFromCrossrefDOI,
    FetchAbstractChain
)

from nomnema.adapters.tasks.sanitize_text import (
    EntryTextSanitizer,
    BibLaTeXEscaper,
    BibKeyNormalizer
)

from nomnema.domain.biblatex import BiblatexDriver

from nomnema.domain.gui.entry_preview import preview_entry_window


class RetrieveOrchestrator(BaseService):
    def __init__(self, cfg: DictConfig, *args, **kwargs):
        self.cfg = cfg

        destination = cfg.get("destination", None)
        if destination is None:
            raise ValueError(f"param `destination` is required")
        self.destination = (
            LocalFolderStorageValidation(destination)
                .perform(mode="check")
            )

        bib_db_path = cfg.get("bib_db", None)
        if bib_db_path is None:
            raise ValueError(f"param `bib_db` is required")
        self.bib_db_path = (
            LocalFileStorageValidation(bib_db_path)
                .perform(mode="check")
            )
        
        self.fetch_bib_entry = FetchBibEntryfromDOI2Bibtex()
        self.entry_text_sanitizer = EntryTextSanitizer()
        self.entry_bib_escaper = BibLaTeXEscaper()
        self.bib_driver = BiblatexDriver(bib_path=self.bib_db_path)
    
    def run(self, *args, **kwargs):
        # file_biblatex = LocalFolderStorageValidation(self.pfname).perform(mode="check")
        #origin = LocalFileStorageValidation(self.origin).perform(mode="check")
        doi_candidate, origin = self._get_doi()
        entry_candidate = self.fetch_bib_entry.perform(doi_candidate, timeout_s=10.0)
        abstract_candidate = self._get_abstract(doi_candidate)
        
        entry_preview = self.bib_driver.append_abstract(entry_candidate, abstract_candidate)

        if entry_preview['doi'] in self.bib_driver.cache_unique_doi:
            raise ValueError(f"Duplicate DOI found: {entry_preview['doi']}")

        bib_entry_preview = self.bib_driver.dict_to_bibtex(entry_preview)
        bib_entry_edited, modified, bib_esc_flag = preview_entry_window(bib_entry_preview)

        if modified:
            entry = self._sanitize_edited(bib_entry_edited, bib_esc_flag)
        else:
            entry = entry_preview
        
        mv_folder = (self.destination/f"{entry['ID']}").as_posix()
        mv_folder = (
            LocalFolderStorageValidation(
                mv_folder,
            ).perform(mode="create")
        )
        fname = entry['ID'] + self.cfg.fname_suffix
        new_loc = mv_folder/f"{fname}{origin.suffix}"
        try:
            new_loc = (
                LocalFileStorageValidation(new_loc.as_posix())
                    .perform(mode="check")
                )
        except FileNotFoundError:
            move(origin, new_loc)
            entry['file'] = f":{new_loc.parent.name}/{new_loc.name}:{new_loc.suffix[1:].upper()}"
            self.bib_driver.add_entry(entry)
            self.bib_driver.save()
            markdown = (
                f"# {entry['title']}\n\n"
                f"**Authors:** {entry['author']}\n\n"
                f"**DOI:** {entry['doi']}\n\n"
                f"## Abstract\n\n{entry['abstract']}\n"
            )
            new_loc.with_suffix(".md").write_text(markdown, encoding="utf-8")
            
            print("Data stored")
        else:
            raise FileExistsError(f"File already exists, set the `fname_suffix` parameter to solve it")

    def _get_doi(self):
        origin = self.cfg.get("origin", None)
        if origin is None:
            raise ValueError(f"param `origin` is required")
        origin = (
            LocalFileStorageValidation(origin)
                .perform(mode="check")
            )
        
        if self.cfg.doi:
            return self.cfg.doi, origin
        else:
            doi_candidate = ExtractDOIfromMarkdown.perform(origin)
            return doi_candidate, origin

    def _get_abstract(self, doi_candidate):
        fetch_chain = FetchAbstractChain(doi_candidate, 'omar@mail.net')
        abstract_candidate, log_abstract_fetch = fetch_chain.run(clear=True)

        if abstract_candidate is None:
            return ""
            #raise ValueError(f"Failed to retrieve abstract for doi: {doi_candidate}")
        
        abstract_candidate = self.entry_text_sanitizer(abstract_candidate)
        abstract_candidate = self.entry_bib_escaper(abstract_candidate, field='abstract')
        return abstract_candidate

    def _sanitize_edited(self, entry_edited, bib_esc_flag):
        parse = self.bib_driver.entry2parser(entry_edited).entries[0]
        parse['abstract'] = self.entry_text_sanitizer(parse['abstract'])
        if bib_esc_flag:
            parse['abstract'] = self.entry_bib_escaper(parse['abstract'], field='abstract')
        return parse
