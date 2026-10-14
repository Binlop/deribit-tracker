from decimal import Decimal

from apps.prices.models import IndexPrice
from apps.prices.repository import IndexPriceRepository

BTC = "btc_usd"
ETH = "eth_usd"

def make_price(ticker: str, timestamp: int, price: str = "100") -> IndexPrice:
    return IndexPrice(ticker=ticker, price=Decimal(price), timestamp=timestamp)


async def seed(session, *prices: IndexPrice) -> None:
    session.add_all(prices)
    await session.flush()
    session.expunge_all() 

async def test_latest_returns_record_with_max_timestamp(session, repository):
    await seed(
        session,
        make_price(BTC, 100, "1"),
        make_price(BTC, 300, "3"),
        make_price(BTC, 200, "2"),
    )

    result = await repository.get_latest_price_by_ticker(BTC)

    assert result is not None
    assert result.timestamp == 300
    assert result.price == Decimal("3")


async def test_latest_ignores_other_ticker_even_if_newer(session, repository):
    await seed(
        session,
        make_price(BTC, 100),
        make_price(ETH, 999),
    )

    result = await repository.get_latest_price_by_ticker(BTC)

    assert result.ticker == BTC
    assert result.timestamp == 100


async def test_latest_returns_none_when_no_data(repository):
    assert await repository.get_latest_price_by_ticker(BTC) is None


# ---------- get_all_prices_by_ticker ----------

async def test_get_all_returns_only_requested_ticker_sorted_desc(session, repository):
    await seed(
        session,
        make_price(BTC, 100),
        make_price(ETH, 150),
        make_price(BTC, 300),
        make_price(BTC, 200),
    )

    result = await repository.get_all_prices_by_ticker(BTC, limit=10, offset=0)

    assert [p.timestamp for p in result] == [300, 200, 100]
    assert {p.ticker for p in result} == {BTC}


async def test_get_all_respects_limit_and_offset(session, repository):
    await seed(session, *(make_price(BTC, ts) for ts in range(1, 6)))

    first_page = await repository.get_all_prices_by_ticker(BTC, limit=2, offset=0)
    second_page = await repository.get_all_prices_by_ticker(BTC, limit=2, offset=2)

    assert [p.timestamp for p in first_page] == [5, 4]
    assert [p.timestamp for p in second_page] == [3, 2]


async def test_get_all_returns_empty_list_for_unknown_ticker(session, repository):
    await seed(session, make_price(BTC, 100))

    assert await repository.get_all_prices_by_ticker("doge_usd", limit=10, offset=0) == []


# ---------- get_prices_by_ticker_and_period ----------

async def test_period_includes_boundaries_and_excludes_outside(session, repository):
    await seed(
        session,
        make_price(BTC, 99),    # до диапазона
        make_price(BTC, 100),   # левая граница
        make_price(BTC, 150),
        make_price(BTC, 200),   # правая граница
        make_price(BTC, 201),   # после диапазона
    )

    result = await repository.get_prices_by_ticker_and_period(
        BTC, start_timestamp=100, end_timestamp=200, limit=10, offset=0
    )

    assert [p.timestamp for p in result] == [100, 150, 200]  # по возрастанию


async def test_period_filters_by_ticker(session, repository):
    await seed(
        session,
        make_price(BTC, 150),
        make_price(ETH, 150),
    )

    result = await repository.get_prices_by_ticker_and_period(
        BTC, start_timestamp=100, end_timestamp=200, limit=10, offset=0
    )

    assert len(result) == 1
    assert result[0].ticker == BTC


async def test_period_respects_limit_and_offset(session, repository):
    await seed(session, *(make_price(BTC, ts) for ts in (100, 110, 120, 130)))

    result = await repository.get_prices_by_ticker_and_period(
        BTC, start_timestamp=100, end_timestamp=130, limit=2, offset=1
    )

    assert [p.timestamp for p in result] == [110, 120]


async def test_period_returns_empty_list_when_nothing_in_range(session, repository):
    await seed(session, make_price(BTC, 100))

    result = await repository.get_prices_by_ticker_and_period(
        BTC, start_timestamp=500, end_timestamp=600, limit=10, offset=0
    )

    assert result == []