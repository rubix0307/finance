import time

from .base import AIProvider
from ai.managers.schemas import ProcessPhotoResponse


class ChatGPTProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def process_photo(self, photo: str) -> ProcessPhotoResponse:
        time.sleep(20)
        return ProcessPhotoResponse(
            status='ok',
            api_key=self.api_key,
        )
