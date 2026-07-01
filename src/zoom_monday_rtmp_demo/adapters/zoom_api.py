from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from zoom_monday_rtmp_demo.config import RtmpConfig, ZoomConfig
from zoom_monday_rtmp_demo.http import request_json


class ZoomApi:
    def __init__(self, config: ZoomConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json",
        }

    def create_meeting(
        self,
        *,
        topic: str,
        duration_minutes: int,
        start_in_minutes: int = 5,
    ) -> dict[str, Any]:
        start_time = (datetime.now(UTC) + timedelta(minutes=start_in_minutes)).replace(microsecond=0)
        payload = {
            "topic": topic,
            "type": 2,
            "start_time": start_time.isoformat().replace("+00:00", "Z"),
            "duration": duration_minutes,
            "settings": {
                "join_before_host": True,
                "waiting_room": False,
                "approval_type": 0,
                "meeting_authentication": False,
                "host_video": True,
                "participant_video": True,
                "audio": "both",
            },
        }
        return request_json(
            "POST",
            f"{self.config.base_url}/users/{self.config.user_id}/meetings",
            headers=self.headers,
            json_body=payload,
        )

    def update_livestream(
        self,
        meeting_id: str,
        *,
        stream_url: str,
        stream_key: str,
        page_url: str,
        resolution: str,
    ) -> None:
        payload = {
            "stream_url": stream_url,
            "stream_key": stream_key,
            "page_url": page_url,
            "resolution": resolution,
        }
        request_json(
            "PATCH",
            f"{self.config.base_url}/meetings/{meeting_id}/livestream",
            headers=self.headers,
            json_body=payload,
        )

    def start_livestream(self, meeting_id: str, *, display_name: str) -> None:
        payload = {
            "action": "start",
            "settings": {
                "active_speaker_name": True,
                "display_name": display_name,
                "layout": "follow_host",
                "close_caption": "burnt-in",
            },
        }
        request_json(
            "PATCH",
            f"{self.config.base_url}/meetings/{meeting_id}/livestream/status",
            headers=self.headers,
            json_body=payload,
        )

    def stop_livestream(self, meeting_id: str) -> None:
        payload = {"action": "stop"}
        request_json(
            "PATCH",
            f"{self.config.base_url}/meetings/{meeting_id}/livestream/status",
            headers=self.headers,
            json_body=payload,
        )

    def get_livestream(self, meeting_id: str) -> dict[str, Any]:
        return request_json(
            "GET",
            f"{self.config.base_url}/meetings/{meeting_id}/livestream",
            headers=self.headers,
        )

    @staticmethod
    def build_stream_urls(rtmp: RtmpConfig, stream_key: str) -> tuple[str, str]:
        stream_url = rtmp.stream_base.rstrip("/")
        page_url = f"{rtmp.page_base.rstrip('/')}/{stream_key}"
        return stream_url, page_url
