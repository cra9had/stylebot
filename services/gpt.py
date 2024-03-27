import asyncio
import os
from typing import Literal, List, Dict
from services.constants import Constants, ENTER_PROMPT_TEMPLATE, GOOD_ANSWER_PROMPT_TEMPLATE, \
    INVALID_ANSWERS

from openai import AsyncOpenAI

BASE_URL = "https://api.proxyapi.ru/openai/v1"


class ChatGPT:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key='sk-H7hZOrms7YmZw4Ak83jsvudN4mk97Ek6', base_url=BASE_URL)

        # TODO: UNCOMMENT THIS
        # self.client = AsyncOpenAI(
        #     api_key=os.environ.get("OPENAI_API_KEY"), base_url=BASE_URL
        # )

    async def _chat(self, prompt: str, context: str | None = None) -> str:
        messages = [
            {
                "role": "user",
                "content": prompt,
            }]

        chat_completion = await self.client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=0.5,
        )
        return chat_completion.choices[0].message.content


    async def get_search_queries(
            self, user_prompt: str, user_sex: Literal["мужчина", "женщина"]
    ) -> list[str] | None:
        prompt = Constants.PROMPT_TEMPLATES.get(ENTER_PROMPT_TEMPLATE).format(user_prompt=user_prompt)

        answer = await self._chat(prompt)

        print(answer)

        if answer in Constants.INVALID_ANSWERS:
            return

        after_answer_prompt = Constants.PROMPT_TEMPLATES.get(GOOD_ANSWER_PROMPT_TEMPLATE).format(gpt_answer=answer)

        final_answer = (await self._chat(after_answer_prompt)).split('\n')

        print(final_answer)

    # return prompts


async def test():
    chat = ChatGPT()
    await chat.get_search_queries("Подбери мне образ из красной рубашки в стиле урбан", user_sex='мужчина')


asyncio.run(test())
