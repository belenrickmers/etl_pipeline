from sqlalchemy import Engine, create_engine
from polars import DataFrame
from etl.utils import get_db_connection_string

def create_db_engine() -> Engine:
    """
    Creates a SQLAlchemy engine for the PostgreSQL database.
    """
    connection_string = get_db_connection_string()
    engine = create_engine(connection_string)
    return engine

def load_df_to_db(df: DataFrame, engine, table_name: str):
    """
    Loads the DataFrame into the database.
    """
    with engine.connect() as connection:
        df.write_database(connection=connection, table_name=table_name, if_table_exists="append")
