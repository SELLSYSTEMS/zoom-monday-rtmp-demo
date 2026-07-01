from __future__ import annotations

import argparse
import json

from zoom_monday_rtmp_demo.adapters.monday_api import MondayApi
from zoom_monday_rtmp_demo.adapters.zoom_api import ZoomApi
from zoom_monday_rtmp_demo.config import MondayConfig, RtmpConfig, ZoomConfig
from zoom_monday_rtmp_demo.services.recording_watcher import wait_for_stable_recording


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=True))


def cmd_zoom_create_meeting(args: argparse.Namespace) -> None:
    zoom = ZoomApi(ZoomConfig.from_env())
    meeting = zoom.create_meeting(
        topic=args.topic,
        duration_minutes=args.duration,
        start_in_minutes=args.start_in_minutes,
    )
    _print(meeting)


def cmd_zoom_provision_meeting(args: argparse.Namespace) -> None:
    zoom = ZoomApi(ZoomConfig.from_env())
    rtmp = RtmpConfig.from_env()
    meeting = zoom.create_meeting(
        topic=args.topic,
        duration_minutes=args.duration,
        start_in_minutes=args.start_in_minutes,
    )
    meeting_id = str(meeting["id"])
    stream_key = (args.stream_key or "").strip() or meeting_id
    stream_url, page_url = zoom.build_stream_urls(rtmp, stream_key)
    zoom.update_livestream(
        meeting_id,
        stream_url=stream_url,
        stream_key=stream_key,
        page_url=page_url,
        resolution=rtmp.resolution,
    )
    _print(
        {
            "meeting": meeting,
            "livestream": {
                "meeting_id": meeting_id,
                "stream_url": stream_url,
                "stream_key": stream_key,
                "page_url": page_url,
                "resolution": rtmp.resolution,
            },
        }
    )


def cmd_zoom_set_livestream(args: argparse.Namespace) -> None:
    zoom = ZoomApi(ZoomConfig.from_env())
    rtmp = RtmpConfig.from_env()
    stream_url, page_url = zoom.build_stream_urls(rtmp, args.stream_key)
    zoom.update_livestream(
        args.meeting_id,
        stream_url=stream_url,
        stream_key=args.stream_key,
        page_url=page_url,
        resolution=rtmp.resolution,
    )
    _print(
        {
            "meeting_id": args.meeting_id,
            "stream_url": stream_url,
            "stream_key": args.stream_key,
            "page_url": page_url,
            "resolution": rtmp.resolution,
        }
    )


def cmd_zoom_start_livestream(args: argparse.Namespace) -> None:
    zoom = ZoomApi(ZoomConfig.from_env())
    zoom.start_livestream(args.meeting_id, display_name=args.display_name)
    _print({"meeting_id": args.meeting_id, "status": "start_requested"})


def cmd_zoom_stop_livestream(args: argparse.Namespace) -> None:
    zoom = ZoomApi(ZoomConfig.from_env())
    zoom.stop_livestream(args.meeting_id)
    _print({"meeting_id": args.meeting_id, "status": "stop_requested"})


def cmd_zoom_get_livestream(args: argparse.Namespace) -> None:
    zoom = ZoomApi(ZoomConfig.from_env())
    _print(zoom.get_livestream(args.meeting_id))


def cmd_monday_set_zoom_link(args: argparse.Namespace) -> None:
    monday = MondayApi(MondayConfig.from_env())
    zoom = ZoomConfig.from_env()
    url = f"{zoom.join_url_base.rstrip('/')}/{args.meeting_id}"
    text = MondayApi.zoom_link_text(args.meeting_id)
    result = monday.set_link_column(
        item_id=args.item_id,
        column_id=monday.config.zoom_link_column_id,
        url=url,
        text=text,
    )
    _print({"item_id": args.item_id, "meeting_id": args.meeting_id, "result": result})


def cmd_monday_set_recording_link(args: argparse.Namespace) -> None:
    monday = MondayApi(MondayConfig.from_env())
    if not monday.config.recording_link_column_id:
        raise ValueError("MONDAY_RECORDING_LINK_COLUMN_ID is required for this command")
    result = monday.set_link_column(
        item_id=args.item_id,
        column_id=monday.config.recording_link_column_id,
        url=args.url,
        text=args.text,
    )
    _print({"item_id": args.item_id, "url": args.url, "result": result})


def cmd_monday_set_status(args: argparse.Namespace) -> None:
    monday = MondayApi(MondayConfig.from_env())
    if not monday.config.status_column_id:
        raise ValueError("MONDAY_STATUS_COLUMN_ID is required for this command")
    result = monday.set_text_column(
        item_id=args.item_id,
        column_id=monday.config.status_column_id,
        text=args.text,
    )
    _print({"item_id": args.item_id, "text": args.text, "result": result})


def cmd_monday_find_by_meeting_id(args: argparse.Namespace) -> None:
    monday = MondayApi(MondayConfig.from_env())
    _print(monday.find_items_by_link_display_text(meeting_id=args.meeting_id))


def cmd_recording_wait(args: argparse.Namespace) -> None:
    rtmp = RtmpConfig.from_env()
    path = wait_for_stable_recording(
        rtmp.recordings_dir,
        args.meeting_id,
        stable_seconds=rtmp.recording_stable_seconds,
        timeout_seconds=args.timeout_seconds,
    )
    _print({"meeting_id": args.meeting_id, "path": str(path)})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Zoom + monday + RTMP demo CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("zoom-create-meeting")
    p.add_argument("--topic", required=True)
    p.add_argument("--duration", required=True, type=int)
    p.add_argument("--start-in-minutes", type=int, default=5)
    p.set_defaults(func=cmd_zoom_create_meeting)

    p = sub.add_parser("zoom-provision-meeting")
    p.add_argument("--topic", required=True)
    p.add_argument("--duration", required=True, type=int)
    p.add_argument("--start-in-minutes", type=int, default=5)
    p.add_argument("--stream-key", default="")
    p.set_defaults(func=cmd_zoom_provision_meeting)

    p = sub.add_parser("zoom-set-livestream")
    p.add_argument("--meeting-id", required=True)
    p.add_argument("--stream-key", required=True)
    p.set_defaults(func=cmd_zoom_set_livestream)

    p = sub.add_parser("zoom-start-livestream")
    p.add_argument("--meeting-id", required=True)
    p.add_argument("--display-name", required=True)
    p.set_defaults(func=cmd_zoom_start_livestream)

    p = sub.add_parser("zoom-stop-livestream")
    p.add_argument("--meeting-id", required=True)
    p.set_defaults(func=cmd_zoom_stop_livestream)

    p = sub.add_parser("zoom-get-livestream")
    p.add_argument("--meeting-id", required=True)
    p.set_defaults(func=cmd_zoom_get_livestream)

    p = sub.add_parser("monday-set-zoom-link")
    p.add_argument("--item-id", required=True)
    p.add_argument("--meeting-id", required=True)
    p.set_defaults(func=cmd_monday_set_zoom_link)

    p = sub.add_parser("monday-set-recording-link")
    p.add_argument("--item-id", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_monday_set_recording_link)

    p = sub.add_parser("monday-set-status")
    p.add_argument("--item-id", required=True)
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_monday_set_status)

    p = sub.add_parser("monday-find-by-meeting-id")
    p.add_argument("--meeting-id", required=True)
    p.set_defaults(func=cmd_monday_find_by_meeting_id)

    p = sub.add_parser("recording-wait")
    p.add_argument("--meeting-id", required=True)
    p.add_argument("--timeout-seconds", type=int, default=600)
    p.set_defaults(func=cmd_recording_wait)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
