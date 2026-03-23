from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from etl.load import _create_db_engine, load_df_to_db


class TestLoad:
	def test_create_db_engine_uses_settings_connection_string(self, mocker):
		settings = mocker.Mock()
		settings.db_connection_string = "postgresql://user:pass@localhost:5432/db"

		engine = object()
		create_engine_mock = mocker.patch("etl.load.create_engine", return_value=engine)

		result = _create_db_engine(settings)

		assert result is engine
		create_engine_mock.assert_called_once_with(settings.db_connection_string)

	def test_load_df_to_db_calls_high_level_dependencies(self, mocker):
		settings = mocker.Mock(db_table_name="coin_market_data", db_schema="public")
		df = mocker.Mock()
		df.to_dicts.return_value = [
			{"id": "bitcoin", "last_updated": "2024-06-01T12:00:00Z", "current_price": 50000.0}
		]
		df.columns = ["id", "last_updated", "current_price"]

		engine = mocker.Mock()
		connection = mocker.Mock()
		engine.begin.return_value = nullcontext(connection)

		create_engine_mock = mocker.patch("etl.load._create_db_engine", return_value=engine)
		table_obj = object()
		table_mock = mocker.patch("etl.load.Table", return_value=table_obj)

		stmt = mocker.Mock()
		stmt.excluded = SimpleNamespace(last_updated="excluded_last_updated", current_price="excluded_current_price")
		stmt.on_conflict_do_update.return_value = stmt

		insert_builder = mocker.Mock()
		insert_builder.values.return_value = stmt
		insert_mock = mocker.patch("etl.load.insert", return_value=insert_builder)

		load_df_to_db(df, settings)

		create_engine_mock.assert_called_once_with(settings)
		table_mock.assert_called_once_with(
			settings.db_table_name,
			mocker.ANY,
			autoload_with=engine,
			schema=settings.db_schema,
		)
		insert_mock.assert_called_once_with(table_obj)
		insert_builder.values.assert_called_once_with(df.to_dicts())
		stmt.on_conflict_do_update.assert_called_once()
		connection.execute.assert_called_once_with(stmt)

	def test_load_df_to_db_builds_conflict_update_without_id(self, mocker):
		settings = mocker.Mock(db_table_name="coin_market_data", db_schema="public")
		df = mocker.Mock()
		df.to_dicts.return_value = [{"id": "bitcoin", "last_updated": "2024-06-01T12:00:00Z", "market_cap": 10.0}]
		df.columns = ["id", "last_updated", "market_cap"]

		engine = mocker.Mock()
		connection = mocker.Mock()
		engine.begin.return_value = nullcontext(connection)

		mocker.patch("etl.load._create_db_engine", return_value=engine)
		mocker.patch("etl.load.Table", return_value=object())

		stmt = mocker.Mock()
		stmt.excluded = SimpleNamespace(last_updated="excluded_last_updated", market_cap="excluded_market_cap")
		stmt.on_conflict_do_update.return_value = stmt
		insert_builder = mocker.Mock(values=mocker.Mock(return_value=stmt))
		mocker.patch("etl.load.insert", return_value=insert_builder)

		load_df_to_db(df, settings)

		_, kwargs = stmt.on_conflict_do_update.call_args
		assert kwargs["index_elements"] == ["id", "last_updated"]
		assert kwargs["set_"] == {
			"last_updated": "excluded_last_updated",
			"market_cap": "excluded_market_cap",
		}
		assert "id" not in kwargs["set_"]

	def test_load_df_to_db_logs_and_reraises_execute_errors(self, mocker):
		settings = mocker.Mock(db_table_name="coin_market_data", db_schema="public")
		df = mocker.Mock()
		df.to_dicts.return_value = [{"id": "bitcoin", "last_updated": "2024-06-01T12:00:00Z"}]
		df.columns = ["id", "last_updated"]

		engine = mocker.Mock()
		connection = mocker.Mock()
		connection.execute.side_effect = RuntimeError("db down")
		engine.begin.return_value = nullcontext(connection)

		mocker.patch("etl.load._create_db_engine", return_value=engine)
		mocker.patch("etl.load.Table", return_value=object())

		stmt = mocker.Mock()
		stmt.excluded = SimpleNamespace(last_updated="excluded_last_updated")
		stmt.on_conflict_do_update.return_value = stmt
		insert_builder = mocker.Mock(values=mocker.Mock(return_value=stmt))
		mocker.patch("etl.load.insert", return_value=insert_builder)
		logger_error = mocker.patch("etl.load.logger.error")

		with pytest.raises(RuntimeError, match="db down"):
			load_df_to_db(df, settings)

		logger_error.assert_called_once()

