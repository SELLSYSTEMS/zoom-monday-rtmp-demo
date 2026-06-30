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
- architecture and setup notes

Planned next:

- server-to-server Zoom OAuth bootstrap
- recording finalization watcher
- post-processing and transcript worker
- optional RTMS migration path

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

## Status

This repo is safe to publish because it contains:

- no production keys
- no tenant-specific IDs as defaults
- no inherited live hostnames as required values

Real deployment secrets belong only on the target instance.
