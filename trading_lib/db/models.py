from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class Strategy(BaseModel):
    """Модель стратегии"""

    __tablename__ = "strategy"
    name = Column(String(255), nullable=False)
    mode = Column(String(50), nullable=False)
    params = Column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f"Strategy(name={self.name}, mode={self.mode}, params={self.params})"


class Position(BaseModel):
    """Модель позиции"""

    __tablename__ = "position"
    strategy_id = Column(ForeignKey(Strategy.id), nullable=False)
    symbol = Column(String(255), nullable=False)
    balance_before = Column(Float)
    balance_after = Column(Float)
    status = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"Position(symbol={self.symbol}, status={self.status})"


class Order(BaseModel):
    """Модель заказа"""

    __tablename__ = "order"
    position_id = Column(ForeignKey(Position.id), nullable=False)
    time = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    side = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    cost = Column(Float, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Order("
            f"{self.position_id=}, {self.time=}, {self.price=}, "
            f"{self.amount=}, {self.side=}, {self.status=}, {self.cost=}"
            f")"
        )
