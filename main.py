
from etl.config import Settings
from etl.extract import call_api
from etl.transform import transform
from etl.load import load_df_to_db

def __main__():
    settings = Settings() # type: ignore[call-arg]
    data = call_api(settings.coingecko_api_url)
    df = transform(data)
    load_df_to_db(df, settings)

if __name__ == "__main__":
    __main__()