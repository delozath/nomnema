from abc import ABC, abstractmethod


from pathlib import Path


class BaseValidation(ABC):
    @abstractmethod
    def perform(self, *args, **kwargs) -> str | Path:
        raise NotImplementedError("method must be implemented")


class BaseLocalStorage(BaseValidation):
    def __init__(self, path: str):
        if not isinstance(path, str):
            raise "path is not a str type"
        self.path = Path(path)