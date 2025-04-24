import io
import json
import os
from typing import Any, Type, Optional, Iterable

from openai import OpenAI
from openai.types.beta import Assistant
from openai.types.beta.threads import (
    ImageFileContentBlockParam,
    TextContentBlockParam,
    MessageContentPartParam,
    Text, Message, MessageContent,
)
from openai.types.beta.threads.run import Usage
from openai.types.beta.threads.run_create_params import AdditionalMessage

from ai.logger import AIUsageLogger
from ai.services.open_ai.decorators import handle_openai_errors
from ai.services.open_ai.managers import TmpFileManager, TmpThreadManager
from ai.services.open_ai.strategies import OpenAI41, OpenAIModelStrategy, OpenAI41Nano
from receipt.models import Receipt
from receipt.schemas import ReceiptSchema


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
        self.analyze_expenses_by_text_assistant: Assistant = self.client.beta.assistants.retrieve(os.getenv('OPENAI_ANALYZE_EXPENSES_BY_TEXT_ASSISTANT_ID', ''))
        self.usage: list[Usage] = []


    def save_usage(
            self,
            usage: Optional[Usage],
            model: Type[OpenAIModelStrategy],
            receipt: Receipt,
        ) -> None:

        if usage:
            self.usage.append(usage)
            AIUsageLogger(model()).log_usage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                receipt=receipt,
            )

    def request(self,
                assistant_id: str,
                poll_interval_ms: int,
                model: Type[OpenAIModelStrategy],
                receipt: Receipt,
                additional_messages: Optional[Iterable[AdditionalMessage]],
                ):

        with TmpThreadManager(self.client) as tmp_thread:
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=tmp_thread.id,
                assistant_id=assistant_id,
                poll_interval_ms=poll_interval_ms,
                additional_messages=additional_messages,
            )

            self.save_usage(
                usage=run.usage,
                model=model,
                receipt=receipt,
            )
            return self._get_response(run.thread_id)



    @handle_openai_errors
    def analyze_user_expenses_by_text(self,
            receipt: Receipt,
            text: str,
            model: Type[OpenAIModelStrategy] = OpenAI41Nano,
            poll_interval_ms: int = 1000,
        ) -> ReceiptSchema:

        response = self.request(
            assistant_id=self.analyze_expenses_by_text_assistant.id,
            poll_interval_ms=poll_interval_ms,
            model=model,
            receipt=receipt,
            additional_messages=[AdditionalMessage(content=text, role='user')],
        )
        return ReceiptSchema(**json.loads(response or ''))

    @handle_openai_errors
    def analyze_receipt(self,
            receipt: Receipt,
            prompt: str = '',
            model: Type[OpenAIModelStrategy] = OpenAI41,
            poll_interval_ms: int = 1000,
        ) -> ReceiptSchema:

        with receipt.photo.open('rb') as photo_rb:
            file_obj = io.BytesIO(photo_rb.read())
            file_obj.name = photo_rb.name
            with TmpFileManager(self.client, create_kwargs={'file': file_obj, 'purpose': 'vision'}) as tmp_file:

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

                response = self.request(
                    assistant_id=self.analyze_receipt_assistant.id,
                    poll_interval_ms=poll_interval_ms,
                    model=model,
                    receipt=receipt,
                    additional_messages=[AdditionalMessage(content=content, role='user')],
                )

                return ReceiptSchema(**json.loads(response or ''))
