from pathlib import Path
from shutil import copy

import pytest
from click import FileError

from nomnema.domain.loader import LoaderPDFFile
from nomnema.domain.move_files import MovePDFFiles


DATA_DIR = Path(__file__).parent.parent / "data"
EXISTING_PDF_FILE = DATA_DIR / "test.pdf"
EXISTING_BIBLATEX_FILE = DATA_DIR / "master_test_entry.bib"


class TestMovePDFFiles:
    def test_pdf_move_moves_file_to_destination(self, tmp_path):
        from markitdown import MarkItDown

        tmp_pdf_file = tmp_path / EXISTING_PDF_FILE.name
        tmp_destination_folder = tmp_path / "mov_test"
        copy(EXISTING_PDF_FILE, tmp_pdf_file)
        tmp_destination_folder.mkdir()

        move = MovePDFFiles(str(tmp_pdf_file), str(tmp_destination_folder))
        move.perform()

        moved_pdf_file = tmp_destination_folder / EXISTING_PDF_FILE.name
        assert not tmp_pdf_file.exists()
        assert moved_pdf_file.is_file()

        loader = LoaderPDFFile(str(moved_pdf_file))
        decoded = loader.load(MarkItDown)
        assert decoded.markdown[126:144] == 'github | @delozath'

    def test_pdf_move_source_missing_raises_file_not_found(self, tmp_path):
        missing_pdf_file = tmp_path / "missing.pdf"
        tmp_destination_folder = tmp_path / "mov_test"
        tmp_destination_folder.mkdir()

        with pytest.raises(FileNotFoundError):
            MovePDFFiles(str(missing_pdf_file), str(tmp_destination_folder))

    def test_pdf_move_destination_missing_raises_not_a_directory(self, tmp_path):
        tmp_pdf_file = tmp_path / EXISTING_PDF_FILE.name
        missing_destination_folder = tmp_path / "missing_folder"
        copy(EXISTING_PDF_FILE, tmp_pdf_file)

        with pytest.raises(NotADirectoryError):
            MovePDFFiles(str(tmp_pdf_file), str(missing_destination_folder))

    def test_pdf_move_invalid_extension_raises_file_error(self, tmp_path):
        tmp_destination_folder = tmp_path / "mov_test"
        tmp_destination_folder.mkdir()

        with pytest.raises(FileError):
            MovePDFFiles(str(EXISTING_BIBLATEX_FILE), str(tmp_destination_folder))
