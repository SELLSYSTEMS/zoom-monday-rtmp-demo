from __future__ import annotations

import json
from typing import Any

from zoom_monday_rtmp_demo.config import MondayConfig
from zoom_monday_rtmp_demo.http import request_json


class MondayApi:
    def __init__(self, config: MondayConfig):
        self.config = config
        self.headers = {
            "Authorization": config.api_token,
            "Content-Type": "application/json",
        }

    def graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        result = request_json("POST", self.config.api_url, headers=self.headers, json_body=payload)
        if result.get("errors"):
            raise RuntimeError(json.dumps(result["errors"]))
        return result

    def set_link_column(self, *, item_id: str, column_id: str, url: str, text: str) -> dict[str, Any]:
        query = """
        mutation ($boardId: ID!, $itemId: ID!, $columnId: String!, $value: JSON!) {
          change_column_value(
            board_id: $boardId,
            item_id: $itemId,
            column_id: $columnId,
            value: $value
          ) {
            id
          }
        }
        """
        value = json.dumps({"url": url, "text": text})
        return self.graphql(
            query,
            {
                "boardId": self.config.board_id,
                "itemId": item_id,
                "columnId": column_id,
                "value": value,
            },
        )

    def set_text_column(self, *, item_id: str, column_id: str, text: str) -> dict[str, Any]:
        query = """
        mutation ($boardId: ID!, $itemId: ID!, $columnId: String!, $value: String!) {
          change_simple_column_value(
            board_id: $boardId,
            item_id: $itemId,
            column_id: $columnId,
            value: $value
          ) {
            id
          }
        }
        """
        return self.graphql(
            query,
            {
                "boardId": self.config.board_id,
                "itemId": item_id,
                "columnId": column_id,
                "value": text,
            },
        )

    def find_items_by_link_display_text(self, *, meeting_id: str) -> list[dict[str, Any]]:
        query = """
        query ($boardId: ID!, $columnId: String!, $meetingId: String!) {
          boards(ids: [$boardId]) {
            items_page(
              limit: 50
              query_params: {
                rules: [{
                  column_id: $columnId
                  compare_value: [$meetingId]
                  operator: contains_text
                }]
              }
            ) {
              items {
                id
                name
                column_values(ids: [$columnId]) {
                  id
                  text
                  value
                }
              }
            }
          }
        }
        """
        data = self.graphql(
            query,
            {
                "boardId": self.config.board_id,
                "columnId": self.config.zoom_link_column_id,
                "meetingId": meeting_id,
            },
        )
        return data["data"]["boards"][0]["items_page"]["items"]

    @staticmethod
    def zoom_link_text(meeting_id: str) -> str:
        return f"Zoom Meeting {meeting_id}"

