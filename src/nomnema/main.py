from typing import Literal

import os
import shutil
import unicodedata
import requests
import dotenv

from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf


import pyperclip
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from markitdown import MarkItDown

from nomnema.adapters import retrieve_orchestrator
from nomnema.adapters.retrieve_orchestrator import RetrieveOrchestrator

@hydra.main(version_base=None, config_path=".", config_name="config")
def orchestrator(cfg: DictConfig) -> None:
    """
    Orchestrate the process of fetching BibTeX entry from DOI in clipboard, copying it back to clipboard,
    and moving the most recent PDF file to the destination directory with the BibTeX key as filename.
    
    bib_database: null
    doi: null
    path_origin: home
    path_destination: home/pdfs
    pfname: none
    """
    RetrieveOrchestrator(cfg).run()
    
        

if __name__ == "__main__":
    # Example DOIs for testing:
    #https://doi.org/10.1136/bmj-2023-078378
    #http://dx.doi.org/10.1136/bmj-2024-082505
    #python folder_latex.py bib_database=home/db.bib doi=10.1136/bmj-2023-078378 path_origin=home path_destination=home/pdfs
    orchestrator()


    #python manage_latex_file.py bib_database=home/db.bib doi=10.1136/bmj-2023-078378 path_origin=home path_destination=home/pdfs