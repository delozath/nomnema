from click import FileError

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from markitdown import MarkItDown

from nomnema.ports.core import BaseLoader

from typing import override

from pathlib import Path

import warnings

from nomnema.domain.validation.local_storage_factory import (
    LocalStorageValidationFactory as store_factory,
)

class LoaderBiblatexFile:
    def __init__(self, path: str, create=False):
        validation = store_factory.create(path, kind='file')
        try:
            path_ = validation.perform(mode='check')
        except FileNotFoundError as e:
            if create:
                db = BibDatabase()
                db.entries = [] 

                path_ = Path(path)
                if path_.suffix != ".bib":
                    raise FileError(f"path provided `{path_}` does not correspond to biblatex file extension")
                
                path_.parent.mkdir(parents=True, exist_ok=True)
                with open(path_.as_posix(), "w", encoding="utf-8") as bibfile:
                    bibtexparser.dump(db, bibfile)
            else:
                raise FileError("The file cannot be created due to create parameter is set as False")
        
        if path_.suffix != ".bib":
            raise FileError(f"path provided `{path_}` does not correspond to biblatex file extension")
        
        bib_str = path_.read_text(encoding="utf-8")
        self.bib_db = bibtexparser.loads(bib_str)

        if not self.bib_db.entries:
            warnings.warn(
            "The provided BibTeX input is empty or contains no valid entries.",
            UserWarning,
            stacklevel=2,
        )


class LoaderPDFFile(BaseLoader):
    VALID_EXT = ['pdf', 'PDF']

    def __init__(self, path: str):
        MODE = 'check' # hard-coded to no create or replace
        validation = store_factory.create(path, kind='file')
        try:
            path_ = validation.perform(mode=MODE)
        except FileNotFoundError as e:
             raise FileNotFoundError("A PDF file must be provided") from e
        else:
            if not path_.suffix[1:] in LoaderPDFFile.VALID_EXT:
                raise FileError(f"File name provided ``{path_.name} has no PDF or pdf extension")
            
            self.path = path_
    
    @override
    def load(self, cls_loader, *args, **kwargs):
        cls_name = cls_loader.__name__
        if cls_name=='MarkItDown':
            inst = cls_loader(*args, **kwargs)
            loader = LoadMarkItDown(inst)
            return loader.load(self.path, *args, **kwargs)
        else:
            raise NotImplementedError(f"Class {cls_name} not implemented")


class LoadMarkItDown(BaseLoader[MarkItDown]):
    def __init__(self, instance):
        self.instance = instance
    
    @override
    def load(self, path: str, *args, **kwargs) -> MarkItDown:
        result = self.instance.convert(path)
        return result
