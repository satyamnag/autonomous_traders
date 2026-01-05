from massive import RESTClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from functools import lru_cache

from database import read_market, write_market

load_dotenv(override = True)

massive_api_key = os.getenv("MASSIVE_API_KEY")

def is_market_open() -> bool:
    client = RESTClient(massive_api_key)
    market_status = client.get_market_status()
    return market_status.market == "open"

def get_all_share_prices_massive_eod() -> tuple[str, dict[str, float]]:
    client = RESTClient(massive_api_key)
    probe = client.get_previous_close_agg("SPY")
    if not probe:
        raise ValueError("Failed to fetch SPY close from API")
    probe = probe[0]
    last_close_date = datetime.fromtimestamp(probe.timestamp / 1000, tz = timezone.utc).date()
    prior_date_str = last_close_date.strftime("%Y-%m-%d")
    results = client.get_grouped_daily_aggs(last_close_date, adjusted = True, include_otc = False)
    market_data = {result.ticker: result.close for result in results}
    if not market_data:
        raise ValueError("Empty market data received from API")
    return prior_date_str, market_data

@lru_cache(maxsize = 2)
def get_market_for_prior_date(prior_date_str: str) -> dict[str, float]:
    market_data = read_market(prior_date_str)
    if not market_data:
        fetched_date_str, market_data = get_all_share_prices_massive_eod()
        write_market(fetched_date_str, market_data)
        return market_data
    return market_data

def get_share_price_massive_eod(symbol: str) -> float:
    today_str = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")
    market_data = get_market_for_prior_date(today_str)
    return market_data.get(symbol, 0.0)

def get_share_price_massive_min(symbol) -> float:
    client = RESTClient(massive_api_key)
    try:
        result = client.get_snapshot_ticker("stocks", symbol)
        return (
            result.min.close
            or result.prev_day.close
            or 0.0
        )
    except (AttributeError, Exception) as e:
        raise ValueError(f"API error for {symbol}: {e}")

def get_share_price(symbol: str) -> float:
    if massive_api_key:
        try:
            return get_share_price_massive_eod(symbol)
        except Exception as e:
            print(
                f"Was not able to use the massive API due to {e}; "
                "using deterministic fallback price"
            )
    print(f"API fallback for {symbol}; using fixed price 150.0")
    return 150.0