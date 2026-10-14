from dataclasses import dataclass
from typing import Annotated
import time
from fastapi import Depends, Query
from db.uow import UnitOfWork, get_uow
from apps.prices.repository import IndexPriceRepository

@dataclass
class Pagination:
    limit: int = 100
    offset: int = 0

def get_pagination(
        limit: int = Query(100, ge=1, le=1000, description="Сколько записей вернуть"),
        offset: int = Query(0, ge=0, description="Сколько записей пропустить"),
) -> Pagination:
    return Pagination(limit=limit, offset=offset)

def get_price_repository(uow: UnitOfWork = Depends(get_uow)) -> IndexPriceRepository:
    return IndexPriceRepository(uow)

def default_start_ts() -> int:
    return int(time.time()) - 1000

def default_end_ts() -> int:
    return int(time.time())

StartTimestamp: Annotated[int, Depends(default_start_ts)]
EndTimestamp: Annotated[int, Depends(default_end_ts)]

PriceRepoDep = Annotated[IndexPriceRepository, Depends(get_price_repository)]
PaginationDep = Annotated[Pagination, Depends(get_pagination)]