import aiohttp
import asyncio
from db.session import CeleryLocalSession
from db.uow  import UnitOfWork
from apps.deribit.client import DeribitClient
from apps.prices.service import IndexPriceService
from core.celery import celery_app

TICKERS = ("btc_usd", "eth_usd")

@celery_app.task(name="apps.deribit.tasks.deribit_price_task")
def deribit_price_task():
    asyncio.run(_fetch_and_save())

async def _fetch_and_save() -> None:
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        client = DeribitClient(session)
        async with CeleryLocalSession() as db:
            async with UnitOfWork(db) as uow:
                service = IndexPriceService(uow, client)
                await service.fetch_and_save(TICKERS)


if __name__ == "__main__":
    deribit_price_task()

