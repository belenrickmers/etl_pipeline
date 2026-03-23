from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class CoinMarketData(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: float
    market_cap_rank: int
    fully_diluted_valuation: float
    total_volume: float
    high_24h: float | None
    low_24h: float | None
    price_change_24h: float | None
    price_change_percentage_24h: float | None
    market_cap_change_24h: float | None
    market_cap_change_percentage_24h: float | None
    circulating_supply: float
    total_supply: float
    ath: float
    ath_change_percentage: float
    ath_date: datetime
    atl: float
    atl_change_percentage: float
    atl_date: datetime
    last_updated: datetime