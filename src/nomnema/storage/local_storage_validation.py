from typing import Literal, override

from pathlib import Path

from nomnema.ports.validation import BaseLocalStorage


class LocalFileStorageValidation(BaseLocalStorage):
    def __init__(self, path):
        super().__init__(path)

    @override
    def perform(self, *, mode: Literal['check', 'create', 'rewrite'] = 'check') -> str | Path:
        """
        Check, create or rewrite the file at `self.path`.

        Parameters
        ----------
        mode : Literal['check', 'create', 'rewrite'], optional
            'check': verify the file exists without modifying it.
            'create': create an empty file; fails if it already exists.
            'rewrite': overwrite an existing file with an empty one; fails if it does not exist.
            Default is 'check'.

        Returns
        -------
        Path
            Path to the checked/created/rewritten file.

        Raises
        -------
        FileNotFoundError
            If mode is 'check' or 'rewrite' and the file does not exist.
        FileExistsError
            If mode is 'create' and the file already exists.
        ValueError
            If mode is not one of 'check', 'create', 'rewrite'.
        """
        exists = self.path.is_file()

        match mode:
            case 'check':
                if not exists:
                    raise FileNotFoundError(f"File does not exist: {self.path}")
            case 'create':
                if exists:
                    raise FileExistsError(f"Cannot create, file already exists: {self.path}")
                self.path.write_text("", encoding="utf-8")
            case 'rewrite':
                if not exists:
                    raise FileNotFoundError(f"Cannot rewrite, file does not exist: {self.path}")
                self.path.write_text("", encoding="utf-8")
            case _:
                raise ValueError(f"Unsupported mode: {mode}")

        return self.path


class LocalFolderStorageValidation(BaseLocalStorage):
    def __init__(self, path):
        super().__init__(path)

    @override
    def perform(self, *, mode: Literal['check', 'create'] = 'check') -> str | Path:
        """
        Check or create the folder at `self.path`.

        Parameters
        ----------
        mode : Literal['check', 'create'], optional
            'check': verify the folder exists without modifying it.
            'create': create the folder, including any missing parents, if it does not exist.
            Default is 'check'.

        Returns
        -------
        Path
            Path to the checked/created folder.

        Raises
        -------
        NotADirectoryError
            If mode is 'check' and the folder does not exist. 
        ValueError
            If mode is not one of 'check', 'create'.
        """
        exists = self.path.is_dir()

        match mode:
            case 'check':
                if not exists:
                    raise NotADirectoryError(f"Folder does not exist: {self.path}")
            case 'create':
                if not exists:
                    self.path.mkdir(parents=True, exist_ok=True)
            case _:
                raise ValueError(f"Unsupported mode: {mode}")

        return self.path
