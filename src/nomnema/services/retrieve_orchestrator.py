from omegaconf import DictConfig

from shutil import move
import re
   

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
    BibKeyNormalizer,
    BibEntryShortNormalizer
)

from nomnema.domain.biblatex import BiblatexDriver, BibEntryParser

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
        self.entry_snorm = BibEntryShortNormalizer()
        self.bibkey_norm = BibKeyNormalizer()
        self.bib_driver = BiblatexDriver(bib_path=self.bib_db_path)
        self.bib_entry_driver = BibEntryParser()
    
    def run(self, *args, **kwargs):
        # file_biblatex = LocalFolderStorageValidation(self.pfname).perform(mode="check")
        #origin = LocalFileStorageValidation(self.origin).perform(mode="check")
        
        doi_candidate, origin = self._get_doi()

        entry_candidate_str = self.fetch_bib_entry.perform(doi_candidate, timeout_s=10.0)
        entry = self.bib_entry_driver(entry_candidate_str)
        if  (grp := self.cfg.group)!="":
            entry['groups'] = grp
        
        abstract_candidate = self._get_abstract(doi_candidate)
        entry = self._compose_entry(entry, abstract_candidate)

        if entry['doi'] in self.bib_driver.cache_unique_doi:
            raise ValueError(f"Duplicate DOI found: {entry['doi']}")

        entry_id = entry['ID']
        entry_preview = self.bib_driver.dict_to_bibtex(entry)
        entry_edited, modified, bib_esc_flag, cancelled = preview_entry_window(entry_preview)

        if cancelled:
            return

        if modified:
            entry = self._sanitize_edited(entry_edited, bib_esc_flag)
        else:
            entry = entry_preview

        new_loc = self._check_folder_structure(entry_id, origin)
        entry = self.bib_entry_driver(entry)
        try:
            new_loc = (
                LocalFileStorageValidation(new_loc.as_posix())
                    .perform(mode="check")
                )
        except FileNotFoundError:
            move(origin, new_loc)
            self._store_bib_file(entry, new_loc)
            self._create_entry_markdown(entry, new_loc)
        else:
            raise FileExistsError(f"File already exists, set the `fname_suffix` parameter to solve it")

    def _store_bib_file(self, entry, new_loc):
        entry['file'] = f":{new_loc.parent.name}/{new_loc.name}:{new_loc.suffix[1:].upper()}"
        self.bib_driver.add_entry(entry)
        self.bib_driver.save()
        print(f"\n\nBiblatex file stored at\n----> {new_loc}")

    def _create_entry_markdown(self, entry, new_loc):
            markdown = (
                f"# {entry['title']}\n\n"
                f"**Authors:** {entry['author']}\n\n"
                f"**DOI:** {entry['doi']}\n\n"
                f"## Abstract\n\n{entry['abstract']}\n"
            )
            
            if new_loc.with_suffix(".md").exists():
                raise FileExistsError(f"File named `{new_loc.with_suffix(".md").name}` is already exists. Set hydra `suffix` flag to proceed")
            new_loc.with_suffix(".md").write_text(markdown, encoding="utf-8")
            print("Markdown stored")

    def _check_folder_structure(self, entry_id, origin):
        mv_folder = (self.destination/f"{entry_id}").as_posix()
        mv_folder = (
            LocalFolderStorageValidation(
                mv_folder,
            ).perform(mode="create")
        )
        fname = entry_id + self.cfg.fname_suffix
        return mv_folder/f"{fname}{origin.suffix}"

    def _compose_entry(self, entry, abstract_candidate):
        abstract = self._format_abstract(abstract_candidate)        
        entry['author'] = self.entry_snorm(entry['author'])
        if (field:='pages') in entry:
            entry[field] = self.entry_snorm(entry[field])
        
        entry['title'] = self.entry_snorm(entry['title'])
        entry['author'] = self.entry_snorm(entry['author'])
        entry['ID'] = self._custom_bibkey(entry, sep='_')
        entry['abstract'] = abstract
        return entry

    def _get_doi(self):
        origin = self.cfg.get("origin", None)
        if origin is None:
            raise ValueError(f"param `origin` is required")
        origin = (
            LocalFileStorageValidation(origin)
                .perform(mode="check")
            )
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

    def _format_abstract(self, abstract):
        return re.sub(r"\.(?=[^\W\d_])", ". ", abstract)

    def _sanitize_edited(self, entry_edited, bib_esc_flag):
        parse = self.bib_entry_driver(entry_edited)
        parse['abstract'] = self.entry_text_sanitizer(parse['abstract'])
        if bib_esc_flag:
            parse['abstract'] = self.entry_bib_escaper(parse['abstract'], field='abstract')
        
        return parse

    def _custom_bibkey(self, entry, sep='_'):
        bibkey = entry['author'].split('and')[0]
        bibkey = re.match(r'^[^ ,]+', bibkey)[0]
        bibkey = self.bibkey_norm(bibkey)
        return  bibkey + sep + entry['year']
