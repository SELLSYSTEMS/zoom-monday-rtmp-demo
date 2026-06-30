from __future__ import annotations

import os
from dataclasses import dataclass


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"missing required environment variable: {name}")
    return value


def _optional(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass(frozen=True)
class ZoomConfig:
    base_url: str
    access_token: str
    user_id: str
    join_url_base: str

    @classmethod
    def from_env(cls) -> "ZoomConfig":
        return cls(
            base_url=_optional("ZOOM_BASE_URL", "https://api.zoom.us/v2"),
            access_token=_required("ZOOM_ACCESS_TOKEN"),
            user_id=_optional("ZOOM_USER_ID", "me"),
            join_url_base=_optional("ZOOM_DEFAULT_JOIN_URL_BASE", "https://zoom.us/j"),
        )


@dataclass(frozen=True)
class MondayConfig:
    api_url: str
    api_token: str
    board_id: str
    zoom_link_column_id: str
    recording_link_column_id: str
    status_column_id: str

    @classmethod
    def from_env(cls) -> "MondayConfig":
        return cls(
            api_url=_optional("MONDAY_API_URL", "https://api.monday.com/v2"),
            api_token=_required("MONDAY_API_TOKEN"),
            board_id=_required("MONDAY_BOARD_ID"),
            zoom_link_column_id=_required("MONDAY_ZOOM_LINK_COLUMN_ID"),
            recording_link_column_id=_optional("MONDAY_RECORDING_LINK_COLUMN_ID"),
            status_column_id=_optional("MONDAY_STATUS_COLUMN_ID"),
        )


@dataclass(frozen=True)
class RtmpConfig:
    stream_base: str
    page_base: str
    resolution: str
    recordings_dir: str
    recording_stable_seconds: int

    @classmethod
    def from_env(cls) -> "RtmpConfig":
        return cls(
            stream_base=_required("RTMP_STREAM_BASE"),
            page_base=_required("RTMP_PAGE_BASE"),
            resolution=_optional("RTMP_RESOLUTION", "720p"),
            recordings_dir=_optional("RECORDINGS_DIR", "/var/lib/zoom-monday-rtmp-demo/recordings"),
            recording_stable_seconds=int(_optional("RECORDING_STABLE_SECONDS", "15")),
        )

