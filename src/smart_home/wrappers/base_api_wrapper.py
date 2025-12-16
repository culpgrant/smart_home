"""Base Async API Wrapper for all wrappers that depend upon APIs."""

from abc import ABC, abstractmethod
from typing import Any

import httpx


class BaseAPI(ABC):
    """Base Async API Wrapper."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
    ) -> None:
        """
        Initialize Base API.

        Args:
            base_url (str): Base URL to use for all API calls
            timeout (float, optional): Seconds to wait till timing out the call.
                Defaults to 10.0.
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
        )

    @abstractmethod
    async def _headers(self) -> dict[str, str]:
        """
        Subclasses implement headers to set with the calls.

        Raises:
            NotImplementedError: Needs to be implemented

        Returns:
            dict[str, str]: headers for api call
        """
        raise NotImplementedError

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Helper _request method that all calls leverage.

        Args:
            method (str): GET, POST, etc...
            path (str): URL path
            params (dict[str, Any] | None, optional): Query Params. Defaults to None.
            json (dict[str, Any] | None, optional): json data. Defaults to None.
            headers (dict[str, Any] | None, optional): Heders. Defaults to None.
            data (dict[str, Any] | None, optional): Data. Defaults to None.

        Returns:
            dict[str, Any]: JSON from result of the call
        """
        headers = headers or await self._headers()
        response = await self._client.request(
            method,
            path,
            headers=headers,
            params=params,
            json=json,
            data=data,
        )

        if response.is_error:
            self.raise_for_status_with_json(response)

        return response.json()

    def raise_for_status_with_json(self, response: httpx.Response) -> httpx.Response:
        """
        Raises an exception if the response is an HTTP error.
        Including the JSON or text content for debugging.

        Args:
            response (httpx.Response): HTTPX Response

        Raises:
            httpx.HTTPStatusError: HTTPX Error with error details

        Returns:
            httpx.Response: HTTP Response
        """
        if response.is_error:
            try:
                content = response.json()
            except ValueError:
                content = response.text
            raise httpx.HTTPStatusError(
                f"HTTP {response.status_code} Error: {content}",
                request=response.request,
                response=response,
            )
        return response

    async def get(self, path: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        GET Call.

        Args:
            path (str): URL Path
            **kwargs(dict): kwargs

        Returns:
            dict[str, Any]: JSON response
        """
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        POST Call.

        Args:
            path (str): URL Path
            **kwargs(dict): kwargs

        Returns:
            dict[str, Any]: JSON response
        """
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        PUT Call.

        Args:
            path (str): URL Path
            **kwargs(dict): kwargs

        Returns:
            dict[str, Any]: JSON response
        """
        return await self._request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        DELETE Call.

        Args:
            path (str): URL Path
            **kwargs(dict): kwargs

        Returns:
            dict[str, Any]: JSON response
        """
        return await self._request("DELETE", path, **kwargs)

    async def close(self) -> None:
        """Close HTTPX Client."""
        await self._client.aclose()
