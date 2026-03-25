from datetime import datetime, timezone

from pydantic import ValidationError
import polars as pl
from etl.models import CoinMarketData
from loguru import logger

logger.add("logs/transform.log", rotation="1 day", retention="7 days", level="ERROR")

    
def _validate_data(data) -> list[CoinMarketData]:
    """
    Validates the data and returns a list of CoinMarketData objects.
    """
    validated_data = []
    for item in data:
        try:
            coin_data = CoinMarketData(**item)
            validated_data.append(coin_data)
        except ValidationError as e:
            logger.error(f"Validation error details: {e.errors()} in item: {item}")
            continue

    return validated_data


def _convert_to_df(validated_data: list[CoinMarketData]) -> pl.DataFrame:
    """
    Converts a list of CoinMarketData objects to a Polars DataFrame.
    """
    if validated_data == []:
        logger.warning("No valid data to convert to DataFrame.")
        return pl.DataFrame()  # Return an empty DataFrame if no valid data
    logger.debug(f"Converting CoinMarketData to dict")
    df = pl.DataFrame([coin.model_dump() for coin in validated_data]).with_columns(pl.col(pl.Float64).round(4), pl.lit(datetime.now(timezone.utc)).alias("ingested_at"))
    logger.debug(f"DataFrame created with shape: {df.shape}")
    logger.debug(f"DataFrame schema: {df.schema}, dataframe head: {df.head()}")

    return df

def transform(data) -> pl.DataFrame:
    """
    Transforms the raw data into a Polars DataFrame.
    """
    validated_data = _validate_data(data)
    df = _convert_to_df(validated_data)
    return df

def validate_df(df: pl.DataFrame) -> None:
    """
    Validates the DataFrame to ensure it has the expected schema and data types.
    """
    try:
        assert df.height > 0, "DataFrame is empty."
        assert (df["current_price"] > 0).all(), "All current_price values must be greater than 0."
        assert df["id"].is_unique().all(), "All id values must be unique."
        logger.info("DataFrame validation successful.")
    except AssertionError as e:
        logger.error(f"DataFrame validation failed: {e}")
        raise