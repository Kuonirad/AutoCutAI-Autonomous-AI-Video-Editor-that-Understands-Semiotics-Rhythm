from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from pathlib import Path
import csv
import logging

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class EditDecision:
    """Atomic cut: inclusive frame range from source media."""

    source_file: str
    src_in: int  # first frame (0-based, inclusive)
    src_out: int  # last frame  (inclusive)
    dst_in: int  # first frame in output timeline

    @property
    def duration(self) -> int:
        # Duration in frames (inclusive range)
        return self.src_out - self.src_in + 1


@dataclass(frozen=True, slots=True)
class RoughCut:
    """Frame-accurate EDL + metadata."""

    decisions: Sequence[EditDecision]
    output_fps: float
    output_resolution: tuple[int, int]  # (w, h)

    @property
    def total_frames(self) -> int:
        if not self.decisions:
            return 0
        # The total duration is the end time of the last decision
        last = self.decisions[-1]
        return last.dst_in + last.duration

    def to_csv(self, path: Path) -> None:
        """Human-readable EDL for inspection (CSV format)."""
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "source_file",
                        "src_in_frame",
                        "src_out_frame",
                        "dst_in_frame",
                        "duration_frames",
                    ]
                )
                for d in self.decisions:
                    writer.writerow(
                        [d.source_file, d.src_in, d.src_out, d.dst_in, d.duration]
                    )
            log.info(f"EDL exported to {path}")
        except IOError as e:
            log.error(f"Failed to export EDL to {path}: {e}")
            raise
