import unittest

from services.gpt import ChatGPT


class ChatGPTTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.gpt = ChatGPT()

    async def test_chat(self):
        answer = await self.gpt._chat("Ping!")
        self.assertEqual(answer, "Pong!")
