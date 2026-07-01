import io
import json
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from zoom_monday_rtmp_demo.cli import cmd_zoom_provision_meeting
from zoom_monday_rtmp_demo.config import RtmpConfig


class CliTests(unittest.TestCase):
    @patch("zoom_monday_rtmp_demo.cli.ZoomApi")
    @patch("zoom_monday_rtmp_demo.cli.ZoomConfig")
    @patch("zoom_monday_rtmp_demo.cli.RtmpConfig")
    def test_zoom_provision_meeting_defaults_stream_key_to_meeting_id(
        self,
        rtmp_config_cls: Mock,
        zoom_config_cls: Mock,
        zoom_api_cls: Mock,
    ) -> None:
        zoom = zoom_api_cls.return_value
        zoom.create_meeting.return_value = {"id": 12345678901, "topic": "Demo"}
        zoom.build_stream_urls.return_value = (
            "rtmp://example.com:49224/live",
            "https://example.com/player/12345678901",
        )
        rtmp_config_cls.from_env.return_value = RtmpConfig(
            stream_base="rtmp://example.com:49224/live",
            page_base="https://example.com/player",
            resolution="720p",
            recordings_dir="/tmp/recordings",
            recording_stable_seconds=15,
        )

        args = Namespace(
            topic="Demo",
            duration=45,
            start_in_minutes=10,
            stream_key="",
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            cmd_zoom_provision_meeting(args)

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["meeting"]["id"], 12345678901)
        self.assertEqual(payload["livestream"]["stream_key"], "12345678901")
        zoom.update_livestream.assert_called_once_with(
            "12345678901",
            stream_url="rtmp://example.com:49224/live",
            stream_key="12345678901",
            page_url="https://example.com/player/12345678901",
            resolution="720p",
        )
        zoom_config_cls.from_env.assert_called_once()
        rtmp_config_cls.from_env.assert_called_once()


if __name__ == "__main__":
    unittest.main()
