from typing import Literal, Optional, Any
from loguru import logger
from .utils import get_query_id_for_search
import aiohttp
import asyncio


DEFAULT_USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
DEFAULT_RETRIES_NUM = 3
DEFAULT_ERROR_SLEEP_TIME = 5    # In seconds


class WildBerriesAPI:
    """Класс для асинхронной работы с private API wildberries"""

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT) -> None:
        self.headers = {"User-Agent": user_agent}
        self._session: Optional[aiohttp.ClientSession] = None

    async def search(self, query: str, page: int = 1) -> dict:
        # TODO: return Products dataclasses
        headers = {
            "x-queryid": get_query_id_for_search()
        }
        params = {
            "ab_testid": "new_pricing",
            "appType": 1,   # 1 - DESKTOP, 32 - ANDROID, 64 - IOS
            "curr": "rub",
            "dest": -1257786,    # MOSCOW
            "query": query,
            "resultset": "catalog",
            "sort": "popular",
            "spp": 30,
            "suppressSpellcheck": "false",
            "uclusters": 1,
        }
        url = "https://search.wb.ru/exactmatch/ru/common/v5/search"
        return await self._request(url=url, request_method="get", params=params, headers=headers)

    async def _get_new_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(headers=self.headers)

    async def _get_session(self) -> Optional[aiohttp.ClientSession]:
        if self._session is None or self._session.closed:
            self._session = await self._get_new_session()

        if not self._session._loop.is_running():
            await self._session.close()
            self._session = await self._get_new_session()
        return self._session

    async def _request(self, url: str, request_method: Literal['get', 'post'] = "get",
                       params: Optional[dict] = None, data: Optional[dict] = None,
                       retries: int = DEFAULT_RETRIES_NUM, **kwargs) -> Any:
        await self._get_session()
        if request_method == "post":
            method = self._session.post
        else:
            method = self._session.get

        try:
            async with method(url=url, params=params, data=data, **kwargs) as response:
                if response.content_type == "application/json":
                    return await response.json()
                else:
                    return response.text
        except aiohttp.ClientError as e:
            logger.error(f"Error occupied while sending request to {url}:\n{e}")
            if retries > 0:
                await asyncio.sleep(DEFAULT_ERROR_SLEEP_TIME)
                return await self._request(url, request_method, params, data, retries - 1, **kwargs)
            raise

    async def close(self):
        await self._session.close()

