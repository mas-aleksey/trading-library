import hmac
import time
from hashlib import sha256

from clients.base import BaseClient
from core.settings import BingXConfig
from schemas.bingx import (
    BingXBalances,
    BingXBalancesResponse,
    BingXCandleResponse,
    BingXOrderHist,
    BingXOrderOut,
    BingXOrderResponse,
    BingXOrdersResponse,
)


class BingXClient(BaseClient[BingXConfig]):
    @property
    def headers(self) -> dict:
        return {
            "X-BX-APIKEY": self.config.API_KEY,
        }

    @staticmethod
    def _parse_param(params_map: dict) -> str:
        sorted_keys = sorted(params_map)
        params_str = "&".join(
            ["%s=%s" % (x, params_map[x]) for x in sorted_keys if params_map[x] is not None]
        )
        if params_str != "":
            return params_str + "&timestamp=" + str(int(time.time() * 1000))
        else:
            return params_str + "timestamp=" + str(int(time.time() * 1000))

    def _make_signed_url(self, path: str, **kwargs) -> str:
        url_params = self._parse_param(kwargs)
        sign = hmac.new(
            self.config.SECRET_KEY.encode("utf-8"),
            url_params.encode("utf-8"),
            digestmod=sha256,
        ).hexdigest()
        return self.get_path(f"{path}?{url_params}&signature={sign}")

    async def get_candles(
        self, symbol: str, interval: str, limit: int, start_time: int = None
    ) -> list[list]:
        url = self._make_signed_url(
            "/openApi/spot/v2/market/kline",
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=start_time,
        )
        base_resp = await self._perform_request("GET", url)
        response = self.load_schema(base_resp.body, BingXCandleResponse)
        return response.data

    async def get_funds(self) -> None:
        url = self._make_signed_url("/openApi/api/v3/capital/deposit/hisrec")
        base_resp = await self._perform_request("GET", url, headers=self.headers)
        for i in base_resp.body:
            print(i)  # noqa T201

    async def get_balances(self) -> BingXBalances:
        url = self._make_signed_url("/openApi/spot/v1/account/balance")
        base_resp = await self._perform_request("GET", url, headers=self.headers)
        response = self.load_schema(base_resp.body, BingXBalancesResponse)
        return response.data

    async def place_order(
        self, symbol: str, side: str, amount: float, client_oid: str
    ) -> BingXOrderOut:
        url = self._make_signed_url(
            "/openApi/spot/v1/trade/order",
            symbol=symbol,
            type="MARKET",
            side=side,
            quantity=amount,
            newClientOrderId=client_oid,
        )
        base_resp = await self._perform_request("POST", url, headers=self.headers)
        response = self.load_schema(base_resp.body, BingXOrderResponse)
        return response.data

    async def get_order_history(self, symbol: str, start_time: int = None) -> list[BingXOrderHist]:
        url = self._make_signed_url(
            "/openApi/spot/v1/trade/historyOrders",
            symbol=symbol,
            startTime=start_time,
            endTime=int(time.time() * 1000),
        )
        base_resp = await self._perform_request("GET", url, headers=self.headers)
        response = self.load_schema(base_resp.body, BingXOrdersResponse)
        return response.data.orders


# async def main() -> None:
#     from core.settings import get_settings
#
#     settings = get_settings()
#     async with BingXClient(settings.BINGX) as client:
#         await client.get_funds()
#
#
# if __name__ == "__main__":
#     import asyncio
#
#     asyncio.run(main())
