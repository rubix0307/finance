from abc import abstractmethod, ABC
from ai.managers.schemes import ProcessPhotoResponse


class AIProvider(ABC):
    @abstractmethod
    def process_photo(self, photo: str) -> ProcessPhotoResponse:
        pass
