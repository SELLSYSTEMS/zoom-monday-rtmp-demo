from __future__ import annotations

import os
import tempfile
import threading
import time
import unittest
from pathlib import Path

from zoom_monday_rtmp_demo.services.recording_watcher import wait_for_stable_recording


class RecordingWatcherTests(unittest.TestCase):
    def test_waits_for_unique_recording_name_to_stabilize(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "81838271355-1782974357.flv"

            def writer() -> None:
                with target.open("wb") as fh:
                    fh.write(b"a" * 128)
                    fh.flush()
                    os.fsync(fh.fileno())
                    time.sleep(1)
                    fh.write(b"b" * 128)
                    fh.flush()
                    os.fsync(fh.fileno())

            thread = threading.Thread(target=writer)
            thread.start()
            path = wait_for_stable_recording(
                tmp,
                "81838271355",
                stable_seconds=1,
                timeout_seconds=10,
            )
            thread.join()
            self.assertEqual(path, target)

    def test_raises_when_no_matching_recording_appears(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(TimeoutError):
                wait_for_stable_recording(
                    tmp,
                    "99999999999",
                    stable_seconds=1,
                    timeout_seconds=1,
                )


if __name__ == "__main__":
    unittest.main()
