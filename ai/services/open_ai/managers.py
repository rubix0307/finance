from typing import Any, Callable

from openai import OpenAI


class BaseTmpResourceManager:
    def __init__(self, client: OpenAI, create_method, delete_method, create_kwargs=None, delete_kwargs=None) -> None:
        if not create_kwargs:
            create_kwargs = {}

        if not delete_kwargs:
            delete_kwargs = {}

        self.client = client
        self.create_method = create_method
        self.delete_method = delete_method
        self.create_kwargs = create_kwargs
        self.delete_kwargs = delete_kwargs
        self.resource = None

    def __enter__(self):
        self.resource = self.create_method(**self.create_kwargs)
        return self.resource

    def __exit__(self, exc_type, exc_value, traceback):
        if self.resource:
            self.delete_method(self.resource.id, **self.delete_kwargs)


class TmpThreadManager(BaseTmpResourceManager):
    def __init__(self, client: OpenAI) -> None:
        super().__init__(
            client=client,
            create_method=client.beta.threads.create,
            delete_method=client.beta.threads.delete
        )

class TmpFileManager(BaseTmpResourceManager):
    def __init__(self, client: OpenAI, create_kwargs: dict[str, Any] | None = None) -> None:
        super().__init__(
            client=client,
            create_kwargs=create_kwargs,
            create_method=client.files.create,
            delete_method=client.files.delete,
        )