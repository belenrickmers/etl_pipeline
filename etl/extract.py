from typing import Any, Optional

import httpx
from loguru import logger

def call_api(base_url: str, params: Optional[dict] = None, headers:Optional[dict] = None) -> Any:
    """
    Calls the API and returns the response as a dictionary.

    Args:
        api_key (str): The API key for authentication.
        url (str): The URL of the API endpoint.

    Returns:
        Any: The response from the API.
    """
    try:
        response = httpx.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        logger.info(f"API call successful: {response.status_code}")
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error occurred while calling the API: {e}")
        return []