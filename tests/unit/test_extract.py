import httpx

from etl.extract import call_api


class TestExtract:
	def test_call_api_returns_json_on_success(self, mocker):
		payload = [{"id": "bitcoin"}]
		response = mocker.Mock()
		response.status_code = 200
		response.raise_for_status.return_value = None
		response.json.return_value = payload

		get_mock = mocker.patch("etl.extract.httpx.get", return_value=response)

		result = call_api(
			"https://api.example.com/coins",
			params={"vs_currency": "usd"},
			headers={"Authorization": "Bearer token"},
		)

		assert result == payload
		get_mock.assert_called_once_with(
			"https://api.example.com/coins",
			params={"vs_currency": "usd"},
			headers={"Authorization": "Bearer token"},
			timeout=10,
		)
		response.raise_for_status.assert_called_once()
		response.json.assert_called_once()

	def test_call_api_returns_empty_list_on_http_status_error(self, mocker):
		request = httpx.Request("GET", "https://api.example.com/coins")
		error_response = httpx.Response(status_code=500, request=request)
		response = mocker.Mock()
		response.raise_for_status.side_effect = httpx.HTTPStatusError(
			"Server error",
			request=request,
			response=error_response,
		)

		mocker.patch("etl.extract.httpx.get", return_value=response)

		result = call_api("https://api.example.com/coins")

		assert result == []

	def test_call_api_returns_empty_list_on_timeout_without_retry(self, mocker):
		request = httpx.Request("GET", "https://api.example.com/coins")
		timeout_error = httpx.TimeoutException("Timed out", request=request)
		get_mock = mocker.patch("etl.extract.httpx.get", side_effect=timeout_error)

		result = call_api("https://api.example.com/coins")

		assert result == []
		assert get_mock.call_count == 1

	def test_call_api_returns_empty_list_on_network_error_without_retry(self, mocker):
		request = httpx.Request("GET", "https://api.example.com/coins")
		network_error = httpx.NetworkError("Network down", request=request)
		get_mock = mocker.patch("etl.extract.httpx.get", side_effect=network_error)

		result = call_api("https://api.example.com/coins")

		assert result == []
		assert get_mock.call_count == 1
