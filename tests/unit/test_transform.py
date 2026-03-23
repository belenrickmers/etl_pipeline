import polars as pl

from etl.models import CoinMarketData
from etl.transform import _convert_to_df, _validate_data, transform


class TestTransform:
    valid_item = {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 50000.123456,
        "market_cap": 1000000000.987654,
        "market_cap_rank": 1,
        "fully_diluted_valuation": 1100000000.876543,
        "total_volume": 50000000.123456,
        "high_24h": 51000.123456,
        "low_24h": 49000.123456,
        "price_change_24h": -1000.123456,
        "price_change_percentage_24h": -2.123456,
        "market_cap_change_24h": -20000000.123456,
        "market_cap_change_percentage_24h": -1.123456,
        "circulating_supply": 19000000.123456,
        "total_supply": 21000000.123456,
        "ath": 69000.123456,
        "ath_change_percentage": -27.123456,
        "ath_date": "2021-11-10T14:24:11Z",
        "atl": 67.123456,
        "atl_change_percentage": 74423.123456,
        "atl_date": "2013-07-06T00:00:00Z",
        "last_updated": "2024-06-01T12:00:00Z",
    }

    def test_validate_data_returns_model_instances_for_valid_rows(self):
        validated_data = _validate_data([self.valid_item])

        assert len(validated_data) == 1
        assert isinstance(validated_data[0], CoinMarketData)
        assert validated_data[0].id == "bitcoin"

    def test_validate_data_skips_invalid_rows(self):
        invalid_item = {
            "id": "badcoin",
            "symbol": "bad",
            "name": "Bad Coin",
            # Missing several required fields on purpose
            "current_price": 1.0,
        }

        validated_data = _validate_data([self.valid_item, invalid_item])

        assert len(validated_data) == 1
        assert validated_data[0].id == "bitcoin"

    def test_convert_to_df_rounds_float_columns_and_adds_ingested_at(self):
        validated_data = _validate_data([self.valid_item])

        df = _convert_to_df(validated_data)

        assert isinstance(df, pl.DataFrame)
        assert df.height == 1
        assert "ingested_at" in df.columns
        assert df["current_price"][0] == 50000.1235
        assert df["market_cap"][0] == 1000000000.9877
        assert df["ingested_at"][0] is not None

    def test_transform_returns_dataframe_with_expected_shape(self):
        df = transform([self.valid_item])

        assert isinstance(df, pl.DataFrame)
        assert df.height == 1
        assert "id" in df.columns
        assert "ingested_at" in df.columns

    def test_transform_with_only_invalid_data_returns_empty_dataframe(self):
        invalid_item = {"id": "badcoin"}

        df = transform([invalid_item])
        assert isinstance(df, pl.DataFrame)
        assert df.height == 0
        assert df.width == 0