import json
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from smart_home.wrappers.base_api_wrapper import BaseAPI


# Setup Test helpers
class FakeBaseAPI(BaseAPI):
    async def _headers(self) -> dict[str, str]:
        return {"header_1": "value_1"}


@pytest.fixture
async def fake_base_api() -> AsyncGenerator[FakeBaseAPI]:
    api_instance = FakeBaseAPI(base_url="https://test.com/", timeout=12)
    yield api_instance
    await api_instance.close()


def create_mock_response(status_code: int) -> httpx.Response:
    content_bytes = json.dumps({"a": "b"}).encode("utf-8")
    mock_request = httpx.Request(method="GET", url="http://mock-url.com")
    return httpx.Response(
        status_code=status_code,
        request=mock_request,
        content=content_bytes,
        # Optional: Add headers to confirm content type
        headers={"Content-Type": "application/json"},
    )


# -------------------
# Actual Tests
# ------------------


def test_base_api_init(fake_base_api: BaseAPI):
    assert fake_base_api.base_url == "https://test.com"
    assert isinstance(fake_base_api._client, httpx.AsyncClient)  # type: ignore


def test_raise_for_status_with_json_failed_response(fake_base_api: BaseAPI):
    response = create_mock_response(status_code=404)
    with pytest.raises(httpx.HTTPStatusError) as exc:
        fake_base_api.raise_for_status_with_json(response)
    assert str(exc.value) == "HTTP 404 Error: {'a': 'b'}"


def test_raise_for_status_with_json_success_response(fake_base_api: BaseAPI):
    response = create_mock_response(status_code=200)
    returned_response = fake_base_api.raise_for_status_with_json(response)
    assert response == returned_response


@pytest.mark.asyncio
@patch("smart_home.wrappers.base_api_wrapper.httpx.AsyncClient")
async def test__request_success(mock_httpx: AsyncMock):
    mock_httpx_client = AsyncMock()
    mock_httpx_client.request.return_value = create_mock_response(status_code=200)
    mock_httpx.return_value = mock_httpx_client

    # cant use fixture
    api_instance = FakeBaseAPI(base_url="https://test.com/")

    result = await api_instance._request(method="GET", path="home")  # type: ignore

    mock_httpx.assert_called_once_with(base_url="https://test.com", timeout=10.0)

    mock_httpx().request.assert_called_once_with(
        "GET",
        "home",
        headers={"header_1": "value_1"},
        params=None,
        json=None,
        data=None,
    )
    assert result == {"a": "b"}


@pytest.mark.asyncio
@patch("smart_home.wrappers.base_api_wrapper.httpx.AsyncClient")
async def test__request_fail(mock_httpx: AsyncMock):
    mock_httpx_client = AsyncMock()
    failed_response = create_mock_response(status_code=404)
    mock_httpx_client.request.return_value = failed_response
    mock_httpx.return_value = mock_httpx_client

    # cant use fixture
    api_instance = FakeBaseAPI(base_url="https://test.com/")

    with pytest.raises(httpx.HTTPStatusError) as exc:
        await api_instance._request(  # type: ignore
            method="GET", path="home", headers={"custom": "headers"}
        )

    assert exc.value.response.status_code == 404

    mock_httpx.assert_called_once_with(base_url="https://test.com", timeout=10.0)

    mock_httpx().request.assert_called_once_with(
        "GET",
        "home",
        headers={"custom": "headers"},
        params=None,
        json=None,
        data=None,
    )


@patch.object(BaseAPI, "_request")
async def test_get(mock_request: AsyncMock, fake_base_api: BaseAPI):
    await fake_base_api.get("home")
    mock_request.assert_called_once_with("GET", "home")


@patch.object(BaseAPI, "_request")
async def test_post(mock_request: AsyncMock, fake_base_api: BaseAPI):
    await fake_base_api.post("home")
    mock_request.assert_called_once_with("POST", "home")


@patch.object(BaseAPI, "_request")
async def test_put(mock_request: AsyncMock, fake_base_api: BaseAPI):
    await fake_base_api.put("home")
    mock_request.assert_called_once_with("PUT", "home")


@patch.object(BaseAPI, "_request")
async def test_delete(mock_request: AsyncMock, fake_base_api: BaseAPI):
    await fake_base_api.delete("home")
    mock_request.assert_called_once_with("DELETE", "home")


@pytest.mark.asyncio
@patch("smart_home.wrappers.base_api_wrapper.httpx.AsyncClient")
async def test_close(mock_httpx: AsyncMock):
    mock_httpx_client = AsyncMock()
    mock_httpx.return_value = mock_httpx_client
    # cant use fixture
    api_instance = FakeBaseAPI(base_url="https://test.com/")

    await api_instance.close()

    mock_httpx.assert_called_once_with(base_url="https://test.com", timeout=10.0)

    mock_httpx().aclose.assert_called_once()
