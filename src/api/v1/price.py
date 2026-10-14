import structlog
from fastapi import APIRouter, status, Query, HTTPException
from fastapi.responses import JSONResponse
from redis_fastapi import CacheBackendDep
from api.deps import PriceRepoDep, PaginationDep, default_start_ts, default_end_ts
from apps.prices.schemas import PriceResponse

router = APIRouter(prefix="/price", tags=["Price"])

log = structlog.get_logger(__name__)

class PriceViews:
    """Эндпоинты для работы с лабораториями."""
    
    @router.get("/", response_model=list[PriceResponse], status_code=status.HTTP_200_OK)
    async def get_all_prices_by_ticker(
        price_repo: PriceRepoDep,
        cache: CacheBackendDep,
        pagination: PaginationDep,
        ticker: str = Query()
    ):
        key = f"deribit_tracker:prices:all:{ticker}:limit={pagination.limit}:offset={pagination.offset}"
        cached = await cache.get(key)
        if cached is not None:
            return JSONResponse(content=cached)
        res = await price_repo.get_all_prices_by_ticker(ticker, pagination.limit, pagination.offset)
        serialized = [PriceResponse.model_validate(item).model_dump(mode="json") for item in res]
        await cache.set(key, serialized, ttl=60)
        return JSONResponse(content=serialized)

    
    @router.get("/latest", response_model=PriceResponse, status_code=status.HTTP_200_OK)
    async def get_latest_price_by_ticker(
        price_repo: PriceRepoDep,
        cache: CacheBackendDep,
        ticker: str = Query()
    ):
        key = f"deribit_tracker:prices:latest:{ticker}"
        cached = await cache.get(key)
        if cached is not None:
            return JSONResponse(content=cached)
        price =  await price_repo.get_latest_price_by_ticker(ticker)
        if price is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No prices found for ticker {ticker}",
            )
        serialized = PriceResponse.model_validate(price).model_dump(mode="json")
        await cache.set(key, serialized, ttl=60)
        return JSONResponse(content=serialized)
    
    @router.get("/by-period", response_model=list[PriceResponse], status_code=status.HTTP_200_OK)
    async def get_prices_by_ticker_and_period(
        price_repo: PriceRepoDep,
        cache: CacheBackendDep,
        pagination: PaginationDep,
        ticker: str = Query(),  
        start_timestamp: int = Query(gt=0, description="Начало периода (UNIX timestamp в секундах)", default_factory=default_start_ts),  
        end_timestamp: int = Query(gt=1, description="Конец периода (UNIX timestamp в секундах)", default_factory=default_end_ts),  
    ):
        if start_timestamp > end_timestamp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_timestamp must be less than or equal to end_timestamp",
            )
        key = f"deribit_tracker:prices:by-period:{ticker}:{start_timestamp}:{end_timestamp}limit={pagination.limit}:offset={pagination.offset}"
        cached = await cache.get(key)
        if cached is not None:
            return JSONResponse(content=cached)
        res = await price_repo.get_prices_by_ticker_and_period(ticker, start_timestamp, end_timestamp, pagination.limit, pagination.offset)
        serialized = [PriceResponse.model_validate(item).model_dump(mode="json") for item in res]
        await cache.set(key, serialized, ttl=3000)
        return JSONResponse(content=serialized)