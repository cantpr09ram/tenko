"""Centralized HTTP header helpers for iClass requests."""

from __future__ import annotations

_COMMON_HEADERS = {
    "sec-ch-ua-platform": '"Android"',
    "accept-language": "zh-Hant",
    "sec-ch-ua": '"Android WebView";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?1",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 14; SM-A146P Build/UP1A.231005.007; wv) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.111 "
        "Mobile Safari/537.36 TronClass/googleplay"
    ),
    "accept": "application/json, text/plain, */*",
    "origin": "http://localhost",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
}


def _copy_headers(source: dict[str, str]) -> dict[str, str]:
    return dict(source)


def session_headers() -> dict[str, str]:
    headers = _copy_headers(_COMMON_HEADERS)
    headers["priority"] = "u=1, i"
    return headers


def number_rollcall_headers() -> dict[str, str]:
    headers = session_headers()
    headers.update(
        {
            "host": "iclass.tku.edu.tw",
            "content-type": "application/json",
            "referer": "http://localhost/",
            "accept-encoding": "gzip, deflate, br, zstd",
        }
    )
    return headers


def radar_headers() -> dict[str, str]:
    headers = _copy_headers(_COMMON_HEADERS)
    headers.update(
        {
            "content-type": "application/json",
            "referer": "http://localhost/",
        }
    )
    return headers
