import unittest

from services.gpt import ChatGPT


class ChatGPTTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.gpt = ChatGPT()

    async def test_search_queries(self):
        queries = await self.gpt.get_search_queries("Хочу образ из джинс", "мужчина")
        self.assertIn("джинсы мужчина", queries[0])

    async def test_chat(self):
        answer = await self.gpt._chat(
            """"Собери мне образ из коричневых шорт и красной футболки"

Выпиши из фразы всю одежду друг за другом через ; в одну строчку, а если таковой нет, напиши NoClothesResponse"""
        )
        self.assertEqual(answer, "Pong!")
