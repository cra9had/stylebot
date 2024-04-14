import asyncio
import json
import os
from typing import Dict
from typing import List
from typing import Literal

from openai import AsyncOpenAI

from services.constants import Constants
from services.constants import ENTER_PROMPT_TEMPLATE
from services.constants import GOOD_ANSWER_PROMPT_TEMPLATE
from services.constants import INVALID_ANSWERS

BASE_URL = "https://api.proxyapi.ru/openai/v1"


class BadClothesException(Exception):
    pass


class ChatGPT:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"), base_url=BASE_URL
        )

    async def _chat(self, prompt: str, context: str | None = None) -> str:
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        chat_completion = await self.client.chat.completions.create(
            messages=messages,
            model="gpt-4-0125-preview",
            temperature=0.5,
        )
        return chat_completion.choices[0].message.content

    async def get_search_queries(
        self, user_prompt: str, user_sex: Literal["мужчина", "женщина"]
    ) -> list[str] | None:
        prompt = Constants.PROMPT_TEMPLATES.get(ENTER_PROMPT_TEMPLATE).format(
            user_prompt=user_prompt
        )
        answer = await self._chat(prompt)
        print(answer)
        if answer in Constants.INVALID_ANSWERS:
            raise BadClothesException()

        try:
            after_answer_prompt = Constants.PROMPT_TEMPLATES.get(
                GOOD_ANSWER_PROMPT_TEMPLATE
            ).format(chat_answer=answer)
            final_answer = (
                (await self._chat(after_answer_prompt))
                .replace("`", "")
                .replace("json", "")
            )
            result = json.loads(final_answer)
            print(result)

            user_sex_text = "мужская" if user_sex == "male" else "женская"
            clothes = [
                position + f" {user_sex_text}" for position in result.get("clothes")
            ]

        except TypeError:
            return None

        return clothes
