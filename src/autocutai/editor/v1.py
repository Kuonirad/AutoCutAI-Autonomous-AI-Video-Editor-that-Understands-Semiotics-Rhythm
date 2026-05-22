# ------------------------------------------------------------
#  AUTOCUTAI : editor/v1 (SimpleBeatSyncPolicy - Robust Implementation)
# ------------------------------------------------------------
from __future__ import annotations

import logging
from typing import Optional

from autocutai.perception.audio import AudioPerception
from autocutai.perception.video import VideoStructurePerception

from .contract import EditDecision, RoughCut
from .utils import BeatGrid

log = logging.getLogger(__name__)

# ---------- tunables ---------------------------------------
# Minimum duration for a shot (input) AND the resulting segment (output)
MIN_SHOT_DURATION_SEC: float = 0.5

# ---------- core algo --------------------------------------


def rough_cut_v1(
    video_perception: VideoStructurePerception,
    audio_perception: AudioPerception,
    source_file: str,
    output_fps: Optional[float] = None,
) -> RoughCut:
    """
    Generates a RoughCut EDL using the SimpleBeatSyncPolicy (V1 Robust).
    Ensures resulting segments meet minimum duration requirements after alignment.
    Frame ranges follow the EditDecision contract: src_out is inclusive.
    """

    if output_fps is None:
        output_fps = video_perception.fps

    # V1 Constraint: No frame rate conversion.
    if abs(output_fps - video_perception.fps) > 0.01:
        log.warning(
            "V1 Editor requires matching FPS. "
            "Forcing output FPS to match input (%s).",
            video_perception.fps,
        )
        output_fps = video_perception.fps

    fps = output_fps

    # Initialize BeatGrid
    try:
        beats = BeatGrid(audio_perception.rhythm_onsets, fps)
    except ValueError as e:
        log.error("Failed to initialize BeatGrid: %s", e)
        return RoughCut(tuple(), output_fps, video_perception.resolution)

    if len(beats) == 0:
        log.warning("No beats detected. Rough cut will be empty.")
        return RoughCut(tuple(), output_fps, video_perception.resolution)

    decisions: list[EditDecision] = []
    dst_cursor = 0  # Current position in the destination timeline (frames)

    log.info(
        "Starting rough cut assembly. Input shots: %s. Beats: %s.",
        len(video_perception.shots),
        len(beats),
    )

    for i, shot in enumerate(video_perception.shots):
        # 1. Filter short input shots
        if shot.duration < MIN_SHOT_DURATION_SEC:
            log.debug("Shot %s dropped (input duration %.2fs).", i, shot.duration)
            continue

        # 2. Align shot start to the nearest beat >= original start
        beat_frame = beats.nearest_on_or_after(shot.start_frame)

        if beat_frame is None:
            # No more beats available. Stop assembly.
            log.info(
                "No beats available after frame %s. Stopping assembly.",
                shot.start_frame,
            )
            break

        src_in = beat_frame
        src_out = shot.end_frame

        # 3. Validate the resulting segment

        # Check if alignment pushes start past the end
        if src_out < src_in:
            # The next beat occurs after the shot ends. Skip.
            log.debug("Shot %s dropped (alignment %s past end %s).", i, src_in, src_out)
            continue

        # CRITICAL: Check if the resulting duration after alignment is still sufficient
        duration_frames = src_out - src_in + 1
        duration_sec = duration_frames / fps

        if duration_sec < MIN_SHOT_DURATION_SEC:
            # The resulting segment after alignment is too short (a sliver). Skip.
            log.debug(
                "Shot %s dropped (output duration %.2fs after alignment).",
                i,
                duration_sec,
            )
            continue

        # 4. Assemble the decision
        decisions.append(
            EditDecision(
                source_file=source_file,
                src_in=src_in,
                src_out=src_out,
                dst_in=dst_cursor,
            )
        )

        # Advance the destination cursor
        dst_cursor += duration_frames

    log.info(
        "Rough cut assembly complete. Decisions: %s. Duration: %.2fs.",
        len(decisions),
        dst_cursor / output_fps,
    )

    return RoughCut(
        decisions=tuple(decisions),
        output_fps=output_fps,
        output_resolution=video_perception.resolution,
    )
