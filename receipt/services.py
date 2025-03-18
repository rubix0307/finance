from ai.managers.api_key import APIKeyManager
from ai.managers.exceptions import KeyNotFoundError
from ai.managers.schemes import ProcessPhotoResponse
from ai.providers.chat_gpt import ChatGPTProvider

API_KEYS = {
    "key1": "abcd-1234",
    "key2": "efgh-5678"
}
api_key_manager = APIKeyManager(API_KEYS)


def process_receipt_photo(photo: str) -> ProcessPhotoResponse | None:
    key_name, identifier = api_key_manager.get_available_key()

    result = None
    try:
        api_key = api_key_manager.get_real_key(key_name)
        if api_key:
            provider = ChatGPTProvider(api_key=api_key)
            result = provider.process_photo(photo)

    except KeyNotFoundError:
        pass

    finally:
        api_key_manager.release_key(key_name, identifier)

    return result
