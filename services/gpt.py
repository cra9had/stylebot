import os

from openai import AsyncOpenAI


BASE_URL = "https://api.proxyapi.ru/openai/v1"


class ChatGPT:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"), base_url=BASE_URL
        )

    def _get_prompt_template(self) -> str: ...

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
