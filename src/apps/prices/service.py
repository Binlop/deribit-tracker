import logging
import asyncio
import time
from collections.abc import Sequence
from db.uow import UnitOfWork
from apps.prices.repository import IndexPriceRepository
from apps.deribit.client import DeribitClient

logger = logging.getLogger(__name__)

class IndexPriceService:

    def __init__(self, uow: UnitOfWork, client: DeribitClient):
        self.index_price_repo = IndexPriceRepository(uow)
        self._uow = uow
        self._client = client

    async def fetch_and_save(self, tickers: Sequence[str]) -> None:
            results = await asyncio.gather(
                *(self._client.get_index_price(t) for t in tickers),
                return_exceptions=True,
            )
            timestamp = int(time.time())

            for ticker, result in zip(tickers, results):
                if isinstance(result, ValueError):
                    logger.error("Failed to fetch %s: %s", ticker, result)
                    continue
                if isinstance(result, BaseException):
                    raise result
                
                await self.index_price_repo.save(ticker=ticker, price=result, timestamp=timestamp)