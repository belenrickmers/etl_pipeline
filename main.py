
import os

from etl.extract import call_api
from etl.utils import load_env_variables


def __main__():
    load_env_variables()
    url = os.getenv("COINGECKO_API_URL")
    if url is None:
        raise ValueError("COINGECKO_API_URL environment variable is not set")
    data = call_api(url)
    print(data)


if __name__ == "__main__":
    __main__()