import os
import unittest

from zoom_monday_rtmp_demo.config import MondayConfig, RtmpConfig, ZoomConfig


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.original)

    def test_zoom_config_from_env(self) -> None:
        os.environ["ZOOM_ACCESS_TOKEN"] = "token"
        cfg = ZoomConfig.from_env()
        self.assertEqual(cfg.user_id, "me")
        self.assertEqual(cfg.base_url, "https://api.zoom.us/v2")

    def test_monday_config_requires_core_values(self) -> None:
        os.environ["MONDAY_API_TOKEN"] = "token"
        os.environ["MONDAY_BOARD_ID"] = "1"
        os.environ["MONDAY_ZOOM_LINK_COLUMN_ID"] = "link"
        cfg = MondayConfig.from_env()
        self.assertEqual(cfg.board_id, "1")

    def test_rtmp_config_reads_defaults(self) -> None:
        os.environ["RTMP_STREAM_BASE"] = "rtmp://example/live"
        os.environ["RTMP_PAGE_BASE"] = "https://example/hls"
        cfg = RtmpConfig.from_env()
        self.assertEqual(cfg.resolution, "720p")
        self.assertEqual(cfg.recording_stable_seconds, 15)


if __name__ == "__main__":
    unittest.main()
