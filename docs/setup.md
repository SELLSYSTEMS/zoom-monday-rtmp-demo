# Setup

## Prerequisites

- Python `3.11+`
- `ffmpeg`
- an RTMP-capable nginx build or equivalent
- a Zoom account and host user that can use custom livestream for meetings
- a monday.com board and API token

## Zoom

You need:

- a valid access token
- a target user ID, usually `me`
- custom livestream enabled for the host user
- a Zoom plan and account policy that actually expose the live-stream setting
- a webhook secret token if you use the included webhook flow

Practical note:

- plain meeting creation can still work on accounts that cannot use custom
  livestream yet
- in that case, `zoom-create-meeting` and `POST /zoom/create-meeting` remain
  useful, while livestream configuration will fail until Zoom account settings
  are fixed

Current code path can mint a fresh Server-to-Server OAuth token automatically
when `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, and `ZOOM_CLIENT_SECRET` are set.

`ZOOM_ACCESS_TOKEN` is still supported as a direct runtime override or fallback.

The recommended app creation and operator handoff walkthrough lives here:

- `docs/zoom_app_setup.md`

## monday.com

You need:

- `MONDAY_API_TOKEN`
- `MONDAY_BOARD_ID`
- a link column for the Zoom URL
- optional link/text columns for recordings and processing status

## RTMP

Use the provided nginx example as a starting point, then adjust:

- hostnames
- TLS termination
- recording path
- HLS exposure

Also decide which deployment mode you are in.

### Plain-host mode

Use the normal RTMP port:

- local listen port:
  - `1935`
- public stream base:
  - `rtmp://host/live`

### Fronted-instance mode

If your platform does not expose local `1935` publicly but already publishes
some other local service port, do this instead:

1. choose the already-published local slot
2. bind RTMP to that local slot
3. move the previous service away from that local port if necessary
4. set `RTMP_STREAM_BASE` to the public published port

Example:

- local RTMP listen port:
  - `1880`
- public published port:
  - `49224`
- public stream base:
  - `rtmp://instance.example.com:49224/live`

Important:

- `RTMP_STREAM_BASE` is the public address Zoom calls
- it does **not** need to equal the local nginx listen port number
- `RTMP_PAGE_BASE` should be the public human-facing live page base
  - with the included player route, use something like:
    - `https://instance.example.com/player`

## Safe deployment rule

Do not put secrets into this repository.

Use one of:

- environment variables
- a local secret file outside the repo
- a systemd `EnvironmentFile`
