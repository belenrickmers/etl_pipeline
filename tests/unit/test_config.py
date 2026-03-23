from etl.config import Settings


class TestConfig:
    def test_db_connection_string_property_builds_expected_postgres_url(self):
        settings = Settings(
            db_host="localhost",
            db_port="5432",
            db_name="coins",
            db_user="etl_user",
            db_password="secret",
            db_table_name="coin_market_data",
            db_schema="public",
            coingecko_api_url="https://api.coingecko.com/api/v3/coins/markets",
        )

        assert (
            settings.db_connection_string
            == "postgresql://etl_user:secret@localhost:5432/coins"
        )
