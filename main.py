
from asyncio.log import logger

from etl.config import Settings
from etl.extract import call_api
from etl.storage import write_parquet_file
from etl.transform import transform
from etl.load import load_df_to_db

def __main__():
    settings = Settings() # type: ignore[call-arg]
    data = call_api(settings.coingecko_api_url)
    
    write_parquet_file(data)
    logger.debug(f"Raw data: {data[:2]}")  # Log the first 2 items of raw data for debugging
    df = transform(data)
    load_df_to_db(df, settings)

if __name__ == "__main__":
    __main__()