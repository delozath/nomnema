import shutil
import uuid
from pathlib import Path

import pytest

from nomnema.storage.local_storage_validation import (
    LocalFileStorageValidation,
    LocalFolderStorageValidation,
)

DATA_DIR = Path(__file__).parent.parent / "data"
EXISTING_FILE = DATA_DIR / "existing_file.txt"
EXISTING_FOLDER = DATA_DIR / "existing_folder"
FILE_TO_REWRITE = DATA_DIR / "file_to_rewrite.txt"


class TestLocalFileStorageValidation:
    def test_check_mode_returns_path_when_file_exists(self):
        storage = LocalFileStorageValidation(str(EXISTING_FILE))

        result = storage.perform(mode="check")

        assert result == EXISTING_FILE

    def test_check_mode_raises_file_not_found_when_file_missing(self, tmp_path):
        target = tmp_path / "missing_document.txt"
        storage = LocalFileStorageValidation(str(target))

        with pytest.raises(FileNotFoundError):
            storage.perform(mode="check")

    def test_create_mode_creates_new_empty_file(self, tmp_path):
        target = tmp_path / "new_document.txt"
        storage = LocalFileStorageValidation(str(target))

        result = storage.perform(mode="create")

        assert result == target
        assert target.is_file()
        assert target.read_text(encoding="utf-8") == ""

    def test_create_mode_raises_file_exists_error_when_file_present(self):
        storage = LocalFileStorageValidation(str(EXISTING_FILE))

        with pytest.raises(FileExistsError):
            storage.perform(mode="create")

    def test_rewrite_mode_overwrites_stored_random_key_and_persists_on_reopen(self, tmp_path):
        target = tmp_path / "document_to_rewrite.txt"
        shutil.copy(FILE_TO_REWRITE, target)
        random_key = uuid.uuid4().hex
        target.write_text(random_key, encoding="utf-8")
        storage = LocalFileStorageValidation(str(target))

        storage.perform(mode="rewrite")

        reopened_content = Path(target).read_text(encoding="utf-8")
        assert reopened_content == ""
        assert reopened_content != random_key

    def test_rewrite_mode_raises_file_not_found_when_file_missing(self, tmp_path):
        target = tmp_path / "missing_document.txt"
        storage = LocalFileStorageValidation(str(target))

        with pytest.raises(FileNotFoundError):
            storage.perform(mode="rewrite")

    def test_perform_raises_value_error_for_unsupported_mode(self, tmp_path):
        target = tmp_path / "any_document.txt"
        storage = LocalFileStorageValidation(str(target))

        with pytest.raises(ValueError):
            storage.perform(mode="unsupported")


class TestLocalFolderStorageValidation:
    def test_check_mode_returns_path_when_folder_exists(self):
        storage = LocalFolderStorageValidation(str(EXISTING_FOLDER))

        result = storage.perform(mode="check")

        assert result == EXISTING_FOLDER

    def test_check_mode_raises_not_a_directory_error_when_folder_missing(self, tmp_path):
        target = tmp_path / "missing_folder"
        storage = LocalFolderStorageValidation(str(target))

        with pytest.raises(NotADirectoryError):
            storage.perform(mode="check")

    def test_create_mode_creates_new_folder(self, tmp_path):
        target = tmp_path / "new_folder"
        storage = LocalFolderStorageValidation(str(target))

        result = storage.perform(mode="create")

        assert result == target
        assert target.is_dir()

    def test_create_mode_creates_nested_parent_folders(self, tmp_path):
        target = tmp_path / "parent_folder" / "child_folder"
        storage = LocalFolderStorageValidation(str(target))

        storage.perform(mode="create")

        assert target.is_dir()

    def test_create_mode_is_idempotent_when_folder_exists(self):
        storage = LocalFolderStorageValidation(str(EXISTING_FOLDER))

        result = storage.perform(mode="create")

        assert result == EXISTING_FOLDER
        assert EXISTING_FOLDER.is_dir()

    def test_perform_raises_value_error_for_unsupported_mode(self, tmp_path):
        storage = LocalFolderStorageValidation(str(tmp_path))

        with pytest.raises(ValueError):
            storage.perform(mode="unsupported")
