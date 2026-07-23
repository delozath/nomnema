from click import FileError

from nomnema.ports.core import BaseLoader
from pathlib import Path
from shutil import copy
from os import remove

from nomnema.domain.validation.local_storage_factory import (
    LocalStorageValidationFactory as store_factory,
)


class MovePDFFiles:
    VALID_EXT = ['pdf', 'PDF']

    def __init__(self, source: str, destination: str):
        MODE = 'check' # hard-coded to no create or replace
        pdf_validation = store_factory.create(source, kind='file')
        to_mov_validation = store_factory.create(destination, kind='folder')
        self.pfname_pdf = pdf_validation.perform(mode=MODE)
        self.mov_folder = to_mov_validation.perform(mode=MODE)

        if not self.pfname_pdf.suffix[1:] in MovePDFFiles.VALID_EXT:
            raise FileError(f"Invalid file extension: {self.pfname_pdf.name}")
    
    def perform(self):
        try:
            new_name = self.mov_folder / self.pfname_pdf.name
            copy(self.pfname_pdf, new_name)
        except Exception as e:
            raise e
        else:
            remove(self.pfname_pdf)
