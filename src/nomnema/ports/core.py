from abc import ABC, abstractmethod

class BaseService[T](ABC):
    @abstractmethod
    def run(self, *args, **kwargs) -> T:
        raise NotImplementedError("method must be implemented")

class BaseExtract[S, T](ABC):
    @abstractmethod
    def perform(self, content: S, *args, **kwargs) -> T:
        raise NotImplementedError("method must be implemented")

class BaseExtractRemote[S, T](ABC):
    __id__: str
    
    @abstractmethod
    def fetch(self, content: S, *args, **kwargs) -> T:
        raise NotImplementedError("method must be implemented")

class BaseFactory[T](ABC):
    @abstractmethod
    def create(self, *args, **kwargs) -> T:
        raise NotImplementedError("method must be implemented")

class BaseLoader[T](ABC):
    @abstractmethod
    def load(self, *args, **kwargs) -> T:
        raise NotImplementedError("method must be implemented")