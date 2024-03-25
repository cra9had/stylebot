import os
from typing import Literal

from openai import AsyncOpenAI

BASE_URL = "https://api.proxyapi.ru/openai/v1"


class ChatGPT:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"), base_url=BASE_URL
        )

    async def _chat(self, prompt: str) -> str:
        chat_completion = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
            temperature=0.5,
        )
        return chat_completion.choices[0].message.content

    async def get_search_queries(
        self, user_prompt: str, user_sex: Literal["female", "male"]
    ) -> list[str]:
        prompt = self._get_prompt_template().format(user_prompt=user_prompt)
        prompts = []
        for query in (await self._chat(prompt)).split("\n"):
            prompts.append(f"{query} {user_sex}")
        return prompts

    @staticmethod
    def _get_prompt_template() -> str:
        return """
            {user_prompt} Какая одежда присутствует в предложении? Пришли лишь одежду, каждую с новой строки без лишних символов и преамбул
        """
