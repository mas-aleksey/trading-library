import hmac
import time
from hashlib import sha256

from async_client import BaseClient
from exchanges.bingx.config import BingXConfig
from exchanges.bingx.schemas import (
    BingXBalances,
    BingXBalancesResponse,
    BingXCandleResponse,
    BingXOrderOut,
    BingXOrderResponse,
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

    def _make_signed_url(self, path: str, **kwargs) -> str:  # noqa: ANN003
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

    async def get_balances(self) -> BingXBalances:
        url = self._make_signed_url("/openApi/spot/v1/account/balance")
        base_resp = await self._perform_request("GET", url, headers=self.headers)
        response = self.load_schema(base_resp.body, BingXBalancesResponse)
        return response.data

    async def place_order(  # noqa: PLR0913
        self, symbol: str, side: str, quantity: float, client_oid: str, order_type: str = "MARKET"
    ) -> BingXOrderOut:
        url = self._make_signed_url(
            "/openApi/spot/v1/trade/order",
            symbol=symbol,
            type=order_type,
            side=side,
            quantity=quantity,
            newClientOrderId=client_oid,
        )
        base_resp = await self._perform_request("POST", url, headers=self.headers)
        response = self.load_schema(base_resp.body, BingXOrderResponse)
        return response.data.order
