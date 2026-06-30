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

## Safe deployment rule

Do not put secrets into this repository.

Use one of:

- environment variables
- a local secret file outside the repo
- a systemd `EnvironmentFile`

