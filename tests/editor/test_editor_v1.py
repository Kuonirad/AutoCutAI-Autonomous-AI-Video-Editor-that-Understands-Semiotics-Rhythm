import logging
from dataclasses import dataclass
from typing import List

# Import implementation and contracts
from autocutai.editor.v1 import rough_cut_v1
from autocutai.editor.utils import BeatGrid
from autocutai.editor.contract import RoughCut, EditDecision
from autocutai.perception.audio import AudioPerception
from autocutai.perception.video import Shot, TransitionType, VideoStructurePerception

log = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Mocks (Standing in for Perception Contracts)
# ------------------------------------------------------------------
# We define minimal mocks to test the editor logic in isolation.


@dataclass
class MockShot:
    duration: float
    start_frame: int
    end_frame: int


@dataclass
class MockVideoStructurePerception:
    shots: List[MockShot]
    fps: float
    resolution: tuple[int, int]


@dataclass
class MockAudioPerception:
    rhythm_onsets: List[float]


# ------------------------------------------------------------------
# Utility Tests (BeatGrid)
# ------------------------------------------------------------------


def test_beatgrid_utility():
    """Verify time-to-frame conversion and efficient searching."""
    fps = 30.0
    # Onsets at 0.5s (F15), 1.0s (F30), 1.5s (F45)
    onsets = [0.5, 1.0, 1.5]
    grid = BeatGrid(onsets, fps)

    assert len(grid) == 3
    assert grid.nearest_on_or_after(0) == 15
    assert grid.nearest_on_or_after(15) == 15  # On the beat
    assert grid.nearest_on_or_after(16) == 30  # After the beat
    assert grid.nearest_on_or_after(46) is None  # No beats left


# ------------------------------------------------------------------
# Policy Tests (V1 Robust)
# ------------------------------------------------------------------


def test_rough_cut_v1_policy_robust():
    """Verify the core V1 policy: Filter short shots, align start to beat, filter short results, assemble."""
    fps = 10.0  # Use 10 FPS for easy frame math

    # Scenario:
    # S1: 0.0-3.0s (F0-29). Dur 3.0s.
    # S2: 3.0-3.4s (F30-33). Dur 0.4s (Input too short).
    # S3: 3.4-6.0s (F34-59). Dur 2.6s.
    # S4: 6.0-6.6s (F60-65). Dur 0.6s (Input OK, but output might be short).

    video = MockVideoStructurePerception(
        shots=[
            MockShot(duration=3.0, start_frame=0, end_frame=29),
            MockShot(duration=0.4, start_frame=30, end_frame=33),
            MockShot(duration=2.6, start_frame=34, end_frame=59),
            MockShot(duration=0.6, start_frame=60, end_frame=65),
        ],
        fps=fps,
        resolution=(1920, 1080),
    )

    # Beats at: 0.5s (F5), 3.5s (F35), 6.3s (F63)
    audio = MockAudioPerception(rhythm_onsets=[0.5, 3.5, 6.3])

    # Expected outcome:
    # S1: Starts 0. Beat 5. Trimmed: 5-29. Dur 25 frames (2.5s). Dst 0.
    # S2: Skipped (Input too short).
    # S3: Starts 34. Beat 35. Trimmed: 35-59. Dur 25 frames (2.5s). Dst 25.
    # S4: Starts 60. Beat 63. Trimmed: 63-65. Dur 3 frames (0.3s). Skipped (Output too short).

    cut: RoughCut = rough_cut_v1(video, audio, "input.mp4")

    assert len(cut.decisions) == 2

    # Decision 1
    assert cut.decisions[0] == EditDecision("input.mp4", src_in=5, src_out=29, dst_in=0)

    # Decision 2
    assert cut.decisions[1] == EditDecision(
        "input.mp4", src_in=35, src_out=59, dst_in=25
    )

    assert cut.total_frames == 50


def test_rough_cut_v1_edge_cases():
    """Test scenarios where beats occur after shots end, or no beats exist."""
    fps = 10.0
    video = MockVideoStructurePerception(
        shots=[MockShot(duration=1.0, start_frame=10, end_frame=19)],
        fps=fps,
        resolution=(1920, 1080),
    )

    # Case 1: Beat after shot ends. Shot ends at F19. Beat at F21 (2.1s).
    audio1 = MockAudioPerception(rhythm_onsets=[2.1])
    cut1 = rough_cut_v1(video, audio1, "input.mp4")
    # Nearest beat >= 10 is 21. src_in=21. src_out=19. Shot skipped.
    assert len(cut1.decisions) == 0

    # Case 2: No beats.
    audio2 = MockAudioPerception(rhythm_onsets=[])
    cut2 = rough_cut_v1(video, audio2, "input.mp4")
    assert len(cut2.decisions) == 0


def test_rough_cut_v1_accepts_public_perception_contracts():
    """The editor should accept the public perception dataclasses directly."""
    video = VideoStructurePerception(
        shots=[
            Shot(
                start_time=0.0,
                end_time=1.0,
                start_frame=0,
                end_frame=9,
                transition_in=TransitionType.HARD_CUT,
                confidence=1.0,
            )
        ],
        fps=10.0,
        duration=1.0,
        resolution=(1280, 720),
    )
    audio = AudioPerception(
        silence_segments=[],
        pacing_curve=[],
        rhythm_onsets=[0.0],
    )

    cut = rough_cut_v1(video, audio, "input.mp4")

    assert cut.output_resolution == (1280, 720)
    assert cut.decisions == (EditDecision("input.mp4", src_in=0, src_out=9, dst_in=0),)
