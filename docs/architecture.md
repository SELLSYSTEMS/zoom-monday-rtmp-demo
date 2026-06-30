# Architecture

## Goal

Provide a small, auditable flow for:

- Zoom meeting creation
- custom livestream configuration
- RTMP recording
- monday.com CRM write-back

## Core flow

1. Create a meeting in Zoom
2. Store the Zoom link in monday.com
3. Configure the meeting's custom livestream target
4. Start the livestream
5. Record the stream on an RTMP server
6. Detect the completed recording
7. Process and publish the result
8. Write result links and status back into monday.com

## Why not Meeting SDK first

The Meeting SDK route is not the right default for this project because:

- current Zoom authorization for external meetings is stricter
- automated or persistent recording is better aligned with RTMS or plain
  custom livestream control
- the historical SDK/browser path created unnecessary operational drift

## Current module boundaries

- `adapters.zoom_api`
  - Zoom REST calls
- `adapters.monday_api`
  - monday GraphQL calls
- `services.recording_watcher`
  - local recording file polling
- `cli`
  - operator-facing command surface

## monday lookup rule

If you need to find items later by meeting ID, embed the meeting ID in the link
display text.

Correct pattern:

```json
{
  "url": "https://zoom.us/j/12345678901",
  "text": "Zoom Meeting 12345678901"
}
```

## RTMP notes

The RTMP layer is intentionally generic:

- dedicated `live` app
- one stream key per meeting or per job
- recordings written to a separate directory
- optional HLS for verification

## Next implementation priorities

1. Add Zoom server-to-server OAuth token bootstrap
2. Add recording conversion and transcript pipeline
3. Add end-to-end integration tests on the target instance
4. Add RTMS migration notes if the account gets RTMS enabled

