# ------------------------------------------------------------
#  AUTOCUTAI : editor/render.py (V1 Stub)
# ------------------------------------------------------------
import logging
from pathlib import Path

# 'av' (PyAV) is the specified dependency.
try:
    import av
except ImportError:
    av = None

from .contract import RoughCut

log = logging.getLogger(__name__)


def render_rough_cut(cut: RoughCut, out_path: Path) -> None:
    """
    (STUB) Renders the RoughCut EDL to a video file.
    """
    if av is None:
        log.warning(
            "Dependency 'av' (PyAV) not found. Rendering capabilities are disabled."
        )

    if not cut.decisions:
        log.info("RoughCut is empty. Nothing to render.")
        return

    log.info(f"Starting render (STUB) of RoughCut to {out_path}...")

    # V1 Stub Implementation: Create placeholder file and CSV.
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w") as f:
            f.write("AutoCutAI V1 Render Stub\n")
            f.write(
                f"Total Frames: {cut.total_frames}, Decisions: {len(cut.decisions)}\n"
            )

        # Save the CSV for inspection
        csv_path = out_path.with_suffix(".csv")
        cut.to_csv(csv_path)

        log.info("Render (STUB) complete.")

    except IOError as e:
        log.error(f"Failed during stub rendering process: {e}")
        raise
