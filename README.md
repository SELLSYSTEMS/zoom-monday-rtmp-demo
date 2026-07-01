# zoom-monday-rtmp-demo

Clean public starter for a `Zoom -> RTMP -> recording -> Monday` workflow.

This repository is intentionally small and environment-driven.

It is designed for:

- creating Zoom meetings via REST
- configuring custom livestream targets
- starting and inspecting livestream sessions
- writing meeting and recording links back to monday.com
- serving as the source of truth for a clean isolated deployment

It is **not** based on the messy historical `Meeting SDK` / browser-join
approach.

## Important deployment distinction

Do not mix these two values:

- the local RTMP listen port inside the instance
- the public ingest URL and port that Zoom will call

In fronted instance environments they can be different.

Example:

- local service listens on `1880`
- public published port is `49224`
- public Zoom ingest becomes:
  - `rtmp://your-instance.example.com:49224/live`

## Why this repo exists

The historical implementation proved the business flow, but it mixed:

- experimental SDK work
- browser automation hacks
- absolute paths
- embedded secrets
- tenant-specific IDs

This repo starts from the cleaner architecture:

1. Zoom REST API creates and configures the meeting
2. custom livestream sends media to RTMP
3. the RTMP server records the stream
4. a processor handles the finished recording
5. monday.com receives meeting and result links

## Current scope

Included now:

- environment-driven config
- Zoom REST adapter
- monday.com GraphQL adapter
- CLI for the critical API steps
- RTMP nginx example
- Debian bootstrap scripts for a clean remote host
- architecture and setup notes

Planned next:

- server-to-server Zoom OAuth bootstrap
- recording finalization watcher
- post-processing and transcript worker
- optional RTMS migration path

## Optional Node-RED lane for fronted instances

If the same instance must keep both:

- public Zoom webhook delivery
- public HLS/player delivery
- public RTMP ingest

there are two workable patterns:

- separate published slots of the same instance
  - one published slot for `Node-RED`
  - one published slot for RTMP
- a fronted HTTPS ingress on the root domain
  - keep `RTMP` on its published high port
  - proxy `/zoom/webhook` and `/player/*` to local `Node-RED`
  - serve `/hls/*` and `/recordings/*` from the fronting app itself or another
    local static layer

A starter `Node-RED` flow is included here:

- `deploy/node_red/zoom_webhook_hls_flow.json`

It provides:

- `POST /zoom/webhook`
  - Zoom endpoint validation response
  - signature verification with `x-zm-signature`
  - JSONL event logging
- `GET /player/:stream`
  - simple player page for `page_url`
- `GET /hls/:stream/index.m3u8`
- `GET /hls/:stream/:segment`

The flow expects:

- `ZOOM_WEBHOOK_SECRET_TOKEN`

in the `Node-RED` environment.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configure

Copy `.env.example` into your secret store or export the variables directly.

The CLI reads environment variables at runtime. No credentials are stored in the
repo.

## Example commands

Create a meeting:

```bash
python -m zoom_monday_rtmp_demo.cli zoom-create-meeting \
  --topic "Demo Call" \
  --duration 60 \
  --start-in-minutes 5
```

Configure livestream:

```bash
python -m zoom_monday_rtmp_demo.cli zoom-set-livestream \
  --meeting-id 12345678901 \
  --stream-key demo-12345678901
```

Start livestream:

```bash
python -m zoom_monday_rtmp_demo.cli zoom-start-livestream \
  --meeting-id 12345678901 \
  --display-name "Demo Call"
```

Write the Zoom link into monday:

```bash
python -m zoom_monday_rtmp_demo.cli monday-set-zoom-link \
  --item-id 1234567890 \
  --meeting-id 12345678901
```

Find monday items by meeting ID:

```bash
python -m zoom_monday_rtmp_demo.cli monday-find-by-meeting-id \
  --meeting-id 12345678901
```

## Important monday.com rule

Link column filters work on the **display text**, not the URL itself.

That means the correct stored format is:

```json
{
  "url": "https://zoom.us/j/12345678901",
  "text": "Zoom Meeting 12345678901"
}
```

## Important Zoom rule

This repo is centered on:

- custom livestream endpoints in the Meetings API

It is not centered on:

- Meeting SDK bots joining external meetings

That is deliberate because Zoom's current authorization rules make the SDK path
worse for automated recording use cases.

## Repo layout

```text
docs/
deploy/
src/zoom_monday_rtmp_demo/
tests/
```

## Remote host bootstrap

This repo includes a Debian-oriented bootstrap script for a clean host:

```bash
sudo bash deploy/scripts/bootstrap_debian_host.sh --domain mondayzoom.sellsystems.agency
```

If your instance platform does **not** expose local `1935` publicly, bind RTMP
to the already-published local slot instead:

```bash
sudo bash deploy/scripts/bootstrap_debian_host.sh \
  --domain mondayzoom.sellsystems.agency \
  --rtmp-listen-port 1880
```

What it does:

- installs `ffmpeg` and `libnginx-mod-rtmp`
- creates runtime directories
- installs nginx RTMP and HLS config
- reloads nginx after config test

What it does **not** do:

- it does not move `Node-RED` off `1880` for you
- it does not discover your platform's public published-port mapping
- it does not prove that Zoom can reach the final public port in your specific
  instance environment

It does **not** install secrets. Zoom and monday credentials must still be
provided separately on the target host.

## Sell.Systems-style fronted instance note

On a plain server, the normal mode is:

- local RTMP listens on `1935`
- Zoom points at public `rtmp://host/live`

On a fronted instance, that assumption can fail.

This repo is prepared for the alternative mode too:

1. choose a local port that the platform already publishes publicly
2. bind RTMP to that local port
3. set `RTMP_STREAM_BASE` to the public URL and public port that Zoom must use
4. move any conflicting local service away from that published slot

For example, if your platform publishes public `:49224` to local `:1880`, then:

- nginx RTMP may listen on local `1880`
- `RTMP_STREAM_BASE` should be:
  - `rtmp://your-instance.example.com:49224/live`

This is still a single-instance deployment. It does not require an external
shared ingress layer.

## Status

This repo is safe to publish because it contains:

- no production keys
- no tenant-specific IDs as defaults
- no inherited live hostnames as required values

Real deployment secrets belong only on the target instance.
