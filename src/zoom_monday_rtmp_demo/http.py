from __future__ import annotations

from typing import Any

import requests


class HttpError(RuntimeError):
    pass


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
) -> Any:
    response = requests.request(method, url, headers=headers, json=json_body, timeout=60)
    if response.status_code >= 400:
        raise HttpError(f"{method} {url} failed: {response.status_code} {response.text}")
    if response.status_code == 204 or not response.text.strip():
        return None
    return response.json()

