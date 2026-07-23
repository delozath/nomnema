from email import message
from pathlib import Path

import pytest
from click import FileError

from nomnema.domain.loader import LoaderBiblatexFile, LoaderPDFFile


DATA_DIR = Path(__file__).parent.parent / "data"
MISSING_BIBLATEX_FILE = DATA_DIR / "master_test.bib"
EXISTING_BIBLATEX_FILE = DATA_DIR / "master_test_entry.bib"
EXISTING_PDF_FILE = DATA_DIR / "test.pdf"


class TestLoaderBiblatexFile:
    def test_loader_biblatex_file_not_exists_and_no_create(self):
        with pytest.raises(FileError):
            loader = LoaderBiblatexFile(str(MISSING_BIBLATEX_FILE))

    def test_loader_biblatex_file_not_exists_and_create(self, tmp_path):
        path = tmp_path / "master_test.bib"
        loader = LoaderBiblatexFile(str(path), create=True)

        assert path.is_file()
        assert loader.bib_db.entries == []

    def test_loader_biblatex_file_create_with_missing_parents(self, tmp_path):
        path = tmp_path / "nested" / "folder" / "master_test.bib"

        loader = LoaderBiblatexFile(str(path), create=True)

        assert path.is_file()
        assert loader.bib_db.entries == []

    def test_loader_biblatex_existing_file(self):
        loader = LoaderBiblatexFile(str(EXISTING_BIBLATEX_FILE))

        entries = loader.bib_db.entries
        assert len(entries) == 1
        assert entries[0]["ID"] == "Vaswani2017"
        assert entries[0]["title"] == "Attention Is All You Need"

    def test_loader_biblatex_existing_file_with_create_enabled(self):
        loader = LoaderBiblatexFile(str(EXISTING_BIBLATEX_FILE), create=True)

        assert len(loader.bib_db.entries) == 1

    def test_loader_biblatex_create_rejects_non_bib_extension(self, tmp_path):
        path = tmp_path / "master_test.txt"

        with pytest.raises(FileError):
            LoaderBiblatexFile(str(path), create=True)

        assert not path.exists()

    def test_loader_biblatex_existing_file_rejects_non_bib_extension(self, tmp_path):
        path = tmp_path / "master_test.txt"
        path.write_text("", encoding="utf-8")

        with pytest.raises(FileError):
            LoaderBiblatexFile(str(path))

    @pytest.mark.parametrize("content", ["", "not valid BibLaTeX content"])
    def test_loader_biblatex_warns_for_empty_or_malformed_content(
        self, tmp_path, content
    ):
        path = tmp_path / "master_test.bib"
        path.write_text(content, encoding="utf-8")
        
        with pytest.warns(UserWarning, match="The provided BibTeX input is empty or contains no valid entries."):
            loader = LoaderBiblatexFile(str(path))
        
        assert loader.bib_db.entries == []


class TestLoaderPDFFile:
    def test_loader_pdf_file_missing(self, tmp_path):
        path = tmp_path / "missing.pdf"
        with pytest.raises(FileNotFoundError):
            loader = LoaderPDFFile(str(path))

    def test_loader_pdf_file_wrong_ext(self):
        with pytest.raises(FileError):
            loader = LoaderPDFFile(str(EXISTING_BIBLATEX_FILE))

    def test_loader_pdf_file_valid_markitdown_decoder(self):
        from markitdown import MarkItDown
        loader = LoaderPDFFile(str(EXISTING_PDF_FILE))
        decoded = loader.load(MarkItDown)
        assert decoded.markdown[126:144] == 'github | @delozath'

    def test_loader_pdf_file_valid_not_implemented_decoder_error(self):
        import numpy as np
        loader = LoaderPDFFile(str(EXISTING_PDF_FILE))
        with pytest.raises(NotImplementedError, match="not implemented"):
            decoded = loader.load(np.ndarray)