from __future__ import annotations

import dataclasses
from enum import Enum


class TransitionType(Enum):
    HARD_CUT = "HARD_CUT"
    FADE = "FADE"
    DISSOLVE = "DISSOLVE"


@dataclasses.dataclass(slots=True)
class Shot:
    start_time: float  # seconds
    end_time: float
    start_frame: int
    end_frame: int
    transition_in: TransitionType
    confidence: float

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


@dataclasses.dataclass(slots=True)
class VideoStructurePerception:
    shots: list[Shot]
    fps: float
    duration: float
    resolution: tuple[int, int]


async def detect_shots(video_path: str) -> VideoStructurePerception:
    raise NotImplementedError("Video shot detection is not implemented yet.")
