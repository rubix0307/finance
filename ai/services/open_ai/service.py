import json
import os
from typing import Any

from openai import OpenAI
from openai.types.beta import Assistant
from openai.types.beta.threads import (
    ImageFileContentBlockParam,
    TextContentBlockParam,
    MessageContentPartParam,
    Text, Message, MessageContent,
)
from openai.types.beta.threads.run import Usage
from ai.services.open_ai.decorators import handle_openai_errors
from ai.services.open_ai.managers import TmpFileManager, TmpThreadManager
from receipt.schemes import ReceiptSchema


class BaseOpenAIMethods:

    @handle_openai_errors
    def __init__(self, **kwargs: dict[str, Any]) -> None:
        self.client = OpenAI()

    @handle_openai_errors
    def _get_response(self, thread_id: str) -> str | None:
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        message: Message = messages.data[0]
        message_content: list[MessageContent] = message.content
        if message_content:
            text: Text = message_content[0].text  # type: ignore
            annotations = text.annotations

            for annotation in annotations:
                text.value = text.value.replace(annotation.text, '')

            response_message = text.value
            return response_message
        return None


class OpenAIService(BaseOpenAIMethods):

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(**kwargs)
        self.analyze_receipt_assistant: Assistant = self.client.beta.assistants.retrieve(os.getenv('OPENAI_ANALYZE_RECEIPT_ASSISTANT_ID', ''))
        self.usage: list[Usage] = []

    @handle_openai_errors
    def analyze_receipt(self, image_path: str, prompt: str = '', poll_interval_ms: int = 1000) -> ReceiptSchema:
        with open(image_path, mode='rb') as file:
            with TmpFileManager(self.client, create_kwargs={'file': file, 'purpose': 'vision'}) as tmp_file:

                file_data: ImageFileContentBlockParam = {
                    'type': 'image_file',
                    'image_file': {
                        'file_id': tmp_file.id,
                        'detail': 'high',
                    }
                }
                content: list[MessageContentPartParam] = [file_data]

                if prompt:
                    text_data: TextContentBlockParam = {'type': 'text', 'text': prompt}
                    content.append(text_data)

                with TmpThreadManager(self.client) as tmp_thread:
                    run = self.client.beta.threads.runs.create_and_poll(
                        thread_id=tmp_thread.id,
                        assistant_id=self.analyze_receipt_assistant.id,
                        poll_interval_ms=poll_interval_ms,
                        additional_messages=[{'content': content, 'role': 'user'}]
                    )
                    if run.usage:
                        self.usage.append(run.usage)

                    response_message = self._get_response(run.thread_id)
                    return ReceiptSchema(**json.loads(response_message or ''))
