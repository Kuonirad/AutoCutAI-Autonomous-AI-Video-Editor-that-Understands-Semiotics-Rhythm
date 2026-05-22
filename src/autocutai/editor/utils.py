import numpy as np
from typing import Optional, List
import logging

log = logging.getLogger(__name__)


class BeatGrid:
    """
    Helper class to manage beat timings and provide efficient frame-accurate lookups (O(log N)).
    """

    def __init__(self, onset_times: List[float], fps: float):
        self.fps = fps
        if fps <= 0:
            raise ValueError("FPS must be positive.")

        # Calculate frame numbers, ensure they are unique, sorted integers.
        # Rounding is crucial for frame accuracy.
        frames = np.round(np.array(onset_times) * fps).astype(int)
        self.onset_frames = np.unique(frames)
        # np.unique returns a sorted array.

        if len(self.onset_frames) == 0:
            log.warning("BeatGrid initialized with zero beats.")

    def nearest_on_or_after(self, frame_num: int) -> Optional[int]:
        """
        Finds the nearest beat frame that occurs on or after the given frame_num.
        """
        # Find the insertion point (side='left' ensures >=)
        idx = np.searchsorted(self.onset_frames, frame_num, side="left")

        if idx < len(self.onset_frames):
            return self.onset_frames[idx]

        # No beats found on or after this frame
        return None

    def __len__(self):
        return len(self.onset_frames)
