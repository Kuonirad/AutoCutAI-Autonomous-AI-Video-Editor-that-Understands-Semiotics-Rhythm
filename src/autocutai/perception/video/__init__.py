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

@dataclasses.dataclass(slots=True)
class VideoStructurePerception:
    shots: list[Shot]
    fps: float
    duration: float

async def detect_shots(video_path: str) -> VideoStructurePerception:
    ...
