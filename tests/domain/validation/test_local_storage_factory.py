import pytest

from nomnema.domain.validation.local_storage_factory import (
    LocalStorageValidationFactory,
)
from nomnema.storage.local_storage_validation import (
    LocalFileStorageValidation,
    LocalFolderStorageValidation,
)


class TestLocalStorageValidationFactory:
    def test_create_with_file_kind_returns_file_storage_validation(self, tmp_path):
        validator = LocalStorageValidationFactory.create(
            str(tmp_path / "document.txt"), kind="file"
        )

        assert isinstance(validator, LocalFileStorageValidation)

    def test_create_with_folder_kind_returns_folder_storage_validation(self, tmp_path):
        validator = LocalStorageValidationFactory.create(
            str(tmp_path / "folder"), kind="folder"
        )

        assert isinstance(validator, LocalFolderStorageValidation)

    def test_create_with_unsupported_kind_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            LocalStorageValidationFactory.create(str(tmp_path), kind="unsupported")

    def test_registry_setter_raises_value_error(self):
        factory = LocalStorageValidationFactory()

        with pytest.raises(ValueError):
            factory.registry = {}
