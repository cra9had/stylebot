from typing import Literal, Optional, Any
from loguru import logger
import aiohttp
import asyncio


DEFAULT_USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
DEFAULT_RETRIES_NUM = 3
DEFAULT_ERROR_SLEEP_TIME = 5    # In seconds


class WildBerriesAPI:
    """Класс для асинхронной работы с private API wildberries"""

    def __init__(self, user_agent: str = "") -> None:
        self.headers = {"User-Agent": user_agent}
        self.session = aiohttp.ClientSession()

    async def _request(self, url: str, request_method: Literal['get', 'post'] = "get",
                       params: Optional[dict] = None, data: Optional[dict] = None,
                       retries: int = DEFAULT_RETRIES_NUM) -> Any:
        if request_method == "post":
            method = self.session.post
        else:
            method = self.session.get

        try:
            response = await method(url=url, params=params, data=data)
        except aiohttp.ClientError as e:
            logger.error(f"Error occupied while sending request to {url}:\n{e}")
            if retries > 0:
                await asyncio.sleep(DEFAULT_ERROR_SLEEP_TIME)
                return await self._request(url, request_method, params, data, retries - 1)
            raise

        return response.json()
