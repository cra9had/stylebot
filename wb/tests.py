import unittest
from .api import WildBerriesAPI


class TestWildBerriesAPI(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.api = WildBerriesAPI()

    async def tearDown(self):
        await self.api.close()

    async def test_base_get_request(self):
        data = {
            "data": {
                "id": 2,
                "email": "janet.weaver@reqres.in",
                "first_name": "Janet",
                "last_name": "Weaver",
                "avatar": "https://reqres.in/img/faces/2-image.jpg"
            },
            "support": {
                "url": "https://reqres.in/#support-heading",
                "text": "To keep ReqRes free, contributions towards server costs are appreciated!"
            }
        }
        response = await self.api._request(
            url="https://reqres.in/api/users/2",
            request_method="get",
        )
        self.assertDictEqual(response, data)
