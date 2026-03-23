from sqlalchemy import Engine, MetaData, Table, create_engine
from sqlalchemy.exc import TimeoutError, DisconnectionError
from sqlalchemy.dialects.postgresql import insert
from polars import DataFrame
from etl.config import Settings
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

def _create_db_engine(settings: Settings) -> Engine:
    """
    Creates a SQLAlchemy engine for the PostgreSQL database.
    """
    engine = create_engine(settings.db_connection_string)
    return engine

@retry(stop=stop_after_attempt(3), reraise=True, wait=wait_exponential(multiplier=1, min=1, max=10), retry=retry_if_exception_type((TimeoutError, DisconnectionError)))
def load_df_to_db(df: DataFrame, settings: Settings):
    """
    Loads the DataFrame into the database.
    """
    engine = _create_db_engine(settings)
    metadata_obj = MetaData()
    table_name = settings.db_table_name
    coin_market_data_table = Table(table_name, metadata_obj, autoload_with=engine, schema=settings.db_schema)
    try:
        with engine.begin() as connection:
            stmt = insert(coin_market_data_table).values(df.to_dicts())
            stmt = stmt.on_conflict_do_update(index_elements=["id", "last_updated"], set_={col: getattr(stmt.excluded, col) for col in df.columns if col != "id"})
            connection.execute(stmt)
    except Exception as e:
        logger.error(f"Error loading data into the database: {e}")
        raise
