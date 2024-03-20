import unittest

from services.gpt import ChatGPT


class ChatGPTTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.gpt = ChatGPT()

    async def test_search_queries(self):
        queries = await self.gpt.get_search_queries(
            "Хочу образ из джинс и футболки и обуви", "мужчина"
        )
        self.assertEqual(len(queries), 3)

    async def test_chat(self):
        answer = await self.gpt._chat("Ping!")
        self.assertEqual(answer, "Pong!")
