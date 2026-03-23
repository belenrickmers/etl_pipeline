import os
from typing import Dict

from dotenv import load_dotenv


###DEPRECATED: These functions are no longer used since we switched to Pydantic's BaseSettings for configuration management. They are kept here for reference but should be removed in future refactoring.

def load_env_variables() -> Dict[str, str]:
    """
    Loads environment variables from the .env file.
    """
    load_dotenv()
    raw_env_vars = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_TABLE_NAME": os.getenv("DB_TABLE_NAME"),
        "COINGECKO_API_URL": os.getenv("COINGECKO_API_URL")
    }
    if not all(raw_env_vars.values()):
        missing_vars = [key for key, value in raw_env_vars.items() if value is None]
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

    # Values are validated above, so they are safe to treat as str.
    env_vars: Dict[str, str] = {key: str(value) for key, value in raw_env_vars.items()}
    return env_vars
    
def get_db_connection_string(env_vars: dict) -> str:
    """Constructs the database connection string from environment variables."""
    user = env_vars["DB_USER"]
    password = env_vars["DB_PASSWORD"]
    host = env_vars["DB_HOST"]
    port = env_vars["DB_PORT"]
    db_name = env_vars["DB_NAME"]
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return connection_string