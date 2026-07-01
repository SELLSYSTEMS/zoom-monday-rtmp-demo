# Setup

## Prerequisites

- Python `3.11+`
- `ffmpeg`
- an RTMP-capable nginx build or equivalent
- a Zoom user with custom livestream permissions
- a monday.com board and API token

## Zoom

You need:

- a valid access token
- a target user ID, usually `me`
- custom livestream enabled for the host user

Current code path uses `ZOOM_ACCESS_TOKEN` directly.

That keeps the bootstrap simple. A later step can add first-class server-to-
server OAuth token generation.

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

## Safe deployment rule

Do not put secrets into this repository.

Use one of:

- environment variables
- a local secret file outside the repo
- a systemd `EnvironmentFile`
