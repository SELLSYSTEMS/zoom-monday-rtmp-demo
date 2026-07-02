from __future__ import annotations

import time
from pathlib import Path


def _pick_recording_candidate(recordings_dir: str, meeting_id: str) -> Path | None:
    root = Path(recordings_dir)
    candidates = sorted(
        root.glob(f"{meeting_id}*.flv"),
        key=lambda path: (path.stat().st_mtime, path.name),
        reverse=True,
    )
    return candidates[0] if candidates else None


def wait_for_stable_recording(recordings_dir: str, meeting_id: str, *, stable_seconds: int, timeout_seconds: int) -> Path:
    deadline = time.time() + timeout_seconds
    target: Path | None = None
    last_size = -1
    stable_since = 0.0

    while time.time() < deadline:
        current = _pick_recording_candidate(recordings_dir, meeting_id)
        if current and current != target:
            target = current
            last_size = -1
            stable_since = 0.0

        if target and target.exists():
            size = target.stat().st_size
            if size > 0 and size == last_size:
                if stable_since == 0.0:
                    stable_since = time.time()
                elif time.time() - stable_since >= stable_seconds:
                    return target
            else:
                stable_since = 0.0
                last_size = size
        time.sleep(3)

    expected = Path(recordings_dir) / f"{meeting_id}*.flv"
    raise TimeoutError(f"recording did not stabilize in time: {expected}")
