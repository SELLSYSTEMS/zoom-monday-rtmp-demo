import unittest
from unittest.mock import Mock, patch

from zoom_monday_rtmp_demo.adapters.zoom_api import ZoomApi
from zoom_monday_rtmp_demo.config import ZoomConfig
from zoom_monday_rtmp_demo.http import HttpError


class ZoomApiTokenTests(unittest.TestCase):
    def test_uses_static_access_token_when_present_without_account_credentials(self) -> None:
        cfg = ZoomConfig(
            base_url="https://api.zoom.us/v2",
            access_token="static-token",
            account_id="",
            client_id="",
            client_secret="",
            token_url="https://zoom.us/oauth/token",
            user_id="me",
            join_url_base="https://zoom.us/j",
        )
        api = ZoomApi(cfg)
        self.assertEqual(api.headers["Authorization"], "Bearer static-token")

    @patch("zoom_monday_rtmp_demo.adapters.zoom_api.requests.post")
    def test_mints_access_token_from_account_credentials(self, post: Mock) -> None:
        response = Mock(status_code=200)
        response.json.return_value = {"access_token": "minted-token"}
        post.return_value = response
        cfg = ZoomConfig(
            base_url="https://api.zoom.us/v2",
            access_token="",
            account_id="acct",
            client_id="client",
            client_secret="secret",
            token_url="https://zoom.us/oauth/token",
            user_id="me",
            join_url_base="https://zoom.us/j",
        )
        api = ZoomApi(cfg)
        self.assertEqual(api.headers["Authorization"], "Bearer minted-token")
        post.assert_called_once()

    @patch("zoom_monday_rtmp_demo.adapters.zoom_api.requests.post")
    def test_raises_when_zoom_token_response_has_no_access_token(self, post: Mock) -> None:
        response = Mock(status_code=200)
        response.json.return_value = {}
        post.return_value = response
        cfg = ZoomConfig(
            base_url="https://api.zoom.us/v2",
            access_token="",
            account_id="acct",
            client_id="client",
            client_secret="secret",
            token_url="https://zoom.us/oauth/token",
            user_id="me",
            join_url_base="https://zoom.us/j",
        )
        with self.assertRaises(HttpError):
            ZoomApi(cfg)


if __name__ == "__main__":
    unittest.main()
