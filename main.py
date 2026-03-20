
import os

from etl.extract import call_api
from etl.utils import load_env_variables
from etl.transform import transform
from loguru import logger

def __main__():
    load_env_variables()
    url = os.getenv("COINGECKO_API_URL")
    if url is None:
        raise ValueError("COINGECKO_API_URL environment variable is not set")
    data = call_api(url)
    df = transform(data)

if __name__ == "__main__":
    __main__()