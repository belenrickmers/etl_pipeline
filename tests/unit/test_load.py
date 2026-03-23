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

	def test_load_df_to_db_executes_upsert_statement(self, mocker):
		settings = mocker.Mock()
		settings.db_table_name = "coin_market_data"
		settings.db_schema = "public"

		df = mocker.Mock()
		df.to_dicts.return_value = [
			{"id": "bitcoin", "last_updated": "2024-06-01T12:00:00Z", "current_price": 50000.0}
		]
		df.columns = ["id", "last_updated", "current_price"]

		engine = mocker.Mock()
		connection = mocker.Mock()
		context_manager = mocker.MagicMock()
		context_manager.__enter__.return_value = connection
		context_manager.__exit__.return_value = None
		engine.begin.return_value = context_manager

		table = object()
		mocker.patch("etl.load._create_db_engine", return_value=engine)
		mocker.patch("etl.load.MetaData", return_value=mocker.Mock())
		table_mock = mocker.patch("etl.load.Table", return_value=table)

		insert_builder = mocker.Mock()
		stmt = mocker.Mock()
		stmt.excluded = SimpleNamespace(last_updated="excluded_last_updated", current_price="excluded_current_price")
		stmt.on_conflict_do_update.return_value = stmt
		insert_builder.values.return_value = stmt
		insert_mock = mocker.patch("etl.load.insert", return_value=insert_builder)

		load_df_to_db(df, settings)

		table_mock.assert_called_once_with(
			settings.db_table_name,
			mocker.ANY,
			autoload_with=engine,
			schema=settings.db_schema,
		)
		insert_mock.assert_called_once_with(table)
		insert_builder.values.assert_called_once_with(df.to_dicts())
		stmt.on_conflict_do_update.assert_called_once()
		connection.execute.assert_called_once_with(stmt)

	def test_load_df_to_db_logs_and_reraises_execute_errors(self, mocker):
		settings = mocker.Mock()
		settings.db_table_name = "coin_market_data"
		settings.db_schema = "public"

		df = mocker.Mock()
		df.to_dicts.return_value = [{"id": "bitcoin", "last_updated": "2024-06-01T12:00:00Z"}]
		df.columns = ["id", "last_updated"]

		engine = mocker.Mock()
		connection = mocker.Mock()
		connection.execute.side_effect = RuntimeError("db down")
		context_manager = mocker.MagicMock()
		context_manager.__enter__.return_value = connection
		context_manager.__exit__.return_value = None
		engine.begin.return_value = context_manager

		mocker.patch("etl.load._create_db_engine", return_value=engine)
		mocker.patch("etl.load.MetaData", return_value=mocker.Mock())
		mocker.patch("etl.load.Table", return_value=object())

		insert_builder = mocker.Mock()
		stmt = mocker.Mock()
		stmt.excluded = SimpleNamespace(last_updated="excluded_last_updated")
		stmt.on_conflict_do_update.return_value = stmt
		insert_builder.values.return_value = stmt
		mocker.patch("etl.load.insert", return_value=insert_builder)
		logger_error = mocker.patch("etl.load.logger.error")

		with pytest.raises(RuntimeError, match="db down"):
			load_df_to_db(df, settings)

		logger_error.assert_called_once()

