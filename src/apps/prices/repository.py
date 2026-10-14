from decimal import Decimal
from sqlalchemy import select
from db.uow import UnitOfWork
from apps.prices.models import IndexPrice

class IndexPriceRepository:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_all_prices_by_ticker(self, ticker: str, limit: int, offset: int) -> list[IndexPrice]:
        stmt = (select(IndexPrice)
                .where(IndexPrice.ticker == ticker)
                .order_by(IndexPrice.timestamp.desc())
                .limit(limit).offset(offset)
                )
        res = await self.uow.db.execute(stmt)
        return res.scalars().all()

    async def get_latest_price_by_ticker(self, ticker) -> IndexPrice|None:
        stmt = (select(IndexPrice)
                .where(IndexPrice.ticker == ticker)
                .order_by(IndexPrice.timestamp.desc())
                .limit(1)
                )
        res = await self.uow.db.execute(stmt)
        return res.scalars().first()

    async def get_prices_by_ticker_and_period(self, ticker: str, 
                                              start_timestamp: int, 
                                              end_timestamp: int, 
                                              limit: int, 
                                              offset: int
                                              ) -> list[IndexPrice]:
        stmt = (select(IndexPrice)
                .where(IndexPrice.ticker == ticker, 
                       IndexPrice.timestamp >= start_timestamp,
                       IndexPrice.timestamp <= end_timestamp)
                .order_by(IndexPrice.timestamp)
                .limit(limit).offset(offset)       
                )
        
        res = await self.uow.db.execute(stmt)
        return res.scalars().all()

    async def save(self, ticker: str, price: Decimal, timestamp: int) -> IndexPrice:
        entity = IndexPrice(ticker=ticker, price=price, timestamp=timestamp)
        self.uow.db.add(entity)
        await self.uow.db.flush()
        return entity