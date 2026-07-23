from typing import Literal

from nomnema.ports.core import BaseFactory
from nomnema.ports.validation import BaseLocalStorage
from nomnema.storage.local_storage_validation import (
    LocalFileStorageValidation,
    LocalFolderStorageValidation,
)


class LocalStorageValidationFactory(BaseFactory[BaseLocalStorage]):
    _REGISTRY = {
        "file": LocalFileStorageValidation,
        "folder": LocalFolderStorageValidation,
    }

    @property
    def registry(self) -> dict:
        return self._REGISTRY

    @registry.setter
    def registry(self, value):
        raise ValueError("Registry cannot is read-only")

    @classmethod
    def create(
        cls,
        path: str,
        *,
        kind: Literal["file", "folder"],
    ) -> BaseLocalStorage:
        """
        Build the local storage validator matching `kind`, decoupling callers
        from the concrete `LocalFileStorageValidation`/`LocalFolderStorageValidation` classes.

        Parameters
        ----------
        path : str
            Path to validate.
        kind : Literal['file', 'folder']
            'file': build a `LocalFileStorageValidation`.
            'folder': build a `LocalFolderStorageValidation`
            Note: add literals as different BaseLocalStages needs to be served by this Factory

        Returns
        -------
        BaseLocalStorage
            The concrete validator instance for the requested kind.

        Raises
        -------
        ValueError
            If `kind` is not one of 'file', 'folder'.
        """
        cls_storage = cls._REGISTRY.get(kind)
        if cls_storage is None:
            raise ValueError(f"No validation class found for kind: {kind}")
        return cls_storage(path)
