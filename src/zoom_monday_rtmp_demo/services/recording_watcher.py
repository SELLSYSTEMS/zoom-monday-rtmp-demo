from __future__ import annotations

import time
from pathlib import Path


def wait_for_stable_recording(recordings_dir: str, meeting_id: str, *, stable_seconds: int, timeout_seconds: int) -> Path:
    target = Path(recordings_dir) / f"{meeting_id}.flv"
    deadline = time.time() + timeout_seconds
    last_size = -1
    stable_since = 0.0

    while time.time() < deadline:
        if target.exists():
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

    raise TimeoutError(f"recording did not stabilize in time: {target}")

