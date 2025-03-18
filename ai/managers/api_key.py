import time
import uuid
import redis

from .exceptions import KeyNotFoundError
from .schemes import Keys, Seconds, KeyName, KeyFull, KeyIdentifier


redis_client = redis.Redis(host='localhost', port=6379, db=0)

class APIKeyManager:
    def __init__(self, keys: Keys, lock_timeout: Seconds = 30):
        self.keys = keys
        self.lock_timeout = lock_timeout

    def acquire_key(self, key_name: KeyName) -> KeyIdentifier | None:
        lock_key = f"lock:api_key:{key_name}"
        identifier: KeyIdentifier = str(uuid.uuid4())
        acquired = redis_client.set(lock_key, value=identifier, nx=True, ex=self.lock_timeout)
        if acquired:
            return identifier
        return None

    @staticmethod
    def release_key(key_name: KeyName, identifier: KeyIdentifier) -> None:
        """
        Releases the lock for the API key if the identifier matches.
        """
        lock_key = f"lock:api_key:{key_name}"
        val = redis_client.get(lock_key)
        if val and val.decode('utf-8') == identifier:
            redis_client.delete(lock_key)

    def get_available_key(self) -> tuple[KeyName, KeyIdentifier]:
        """
        Gets an available API key.
        If all keys are occupied, waits for release and retries.
        """
        while True:
            for key_name in self.keys.keys():
                identifier = self.acquire_key(key_name)
                if identifier:
                    return key_name, identifier
            time.sleep(1)

    def get_real_key(self, key_name: KeyName) -> KeyFull:
        """
        Converts a key name (“key1”) to a real API key.
        Raises KeyNotFoundError if the key does not exist.
        """
        if key_name not in self.keys:
            raise KeyNotFoundError(f"Key '{key_name}' not found in API key manager.")

        return self.keys[key_name]
