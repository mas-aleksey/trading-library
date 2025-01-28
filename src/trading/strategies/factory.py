from uuid import UUID

from db.db_connector import DatabaseConnector
from schemas.enums import StrategyType
from schemas.params import WorkerParams
from trading.chart import Chart
from trading.exchanges.base import BaseExchange
from trading.notifier import NotifyService
from trading.strategies.base import BaseStrategy
from trading.strategies.knife import KnifeStrategy


class StrategyFactory:
    STRATEGIES = {
        StrategyType.KNIFE: "_knife_strategy",
    }

    @staticmethod
    def _knife_strategy(  # noqa: PLR0913
        strategy_id: UUID,
        params: WorkerParams,
        exchange: BaseExchange,
        db: DatabaseConnector,
        notifier: NotifyService,
        online_check: bool,
    ) -> KnifeStrategy:
        return KnifeStrategy(
            strategy_id=strategy_id,
            symbol=params.symbol,
            chart=Chart.new(params.chart),
            exchange=exchange,
            db=db,
            notifier=notifier,
            online_check=online_check,
            **params.strategy.params,
        )

    @classmethod
    def new(  # noqa: PLR0913
        cls,
        strategy_id: UUID,
        params: WorkerParams,
        exchange: BaseExchange,
        db: DatabaseConnector,
        notifier: NotifyService,
        online_check: bool = False,
    ) -> BaseStrategy:
        return getattr(cls, cls.STRATEGIES[params.strategy.class_])(
            strategy_id, params, exchange, db, notifier, online_check
        )
