from decimal import Decimal
from sqlalchemy import String, Numeric, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column
from db.session import Base

class IndexPrice(Base):
    __tablename__ = "index_prices"
    __table_args__ = (
        Index("ix_index_prices_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(50))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 10))
    timestamp: Mapped[int] = mapped_column(BigInteger)

    def __str__(self):
        return f'Currency: {self.ticker}, price: {self.price}'

