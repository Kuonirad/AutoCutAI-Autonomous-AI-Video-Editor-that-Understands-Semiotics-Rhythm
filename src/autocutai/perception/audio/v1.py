# ------------------------------------------------------------
#  AUTOCUTAI : perception/audio/v1
# ------------------------------------------------------------
import asyncio
import dataclasses
import logging

import numpy as np
import soundfile as sf
from scipy.signal import find_peaks, stft as scipy_stft

# Configure logging
log = logging.getLogger(__name__)


# ---------- contract ---------------------------------------
@dataclasses.dataclass(slots=True)
class AudioPerception:
    silence_segments: list[tuple[float, float]]  # (start_sec, end_sec)
    pacing_curve: list[float]  # RMS energy per window
    rhythm_onsets: list[float]  # seconds


# ---------- tunables ---------------------------------------
SILENCE_THRESHOLD_DB: float = -30.0  # relative to full-scale
WINDOW_SEC: float = 0.025  # 25 ms Hamming window
HOP_SEC: float = 0.010  # 10 ms hop
ONSET_THRESHOLD: float = 0.15  # normalized onset strength
MIN_SILENCE_SEC: float = 0.25  # ignore gaps < 250 ms


# ---------- helpers ----------------------------------------
def _db2amp(db: float) -> float:
    return 10 ** (db / 20)


def _rms_energy(y: np.ndarray, win_size: int, hop_size: int) -> np.ndarray:
    """Rolling RMS via strided tricks."""
    if len(y) < win_size:
        return np.array([])
    num_frames = 1 + (len(y) - win_size) // hop_size
    shape = (num_frames, win_size)
    # Ensure contiguous array for striding
    y = np.ascontiguousarray(y)
    strides = (y.strides[0] * hop_size, y.strides[0])
    try:
        frames = np.lib.stride_tricks.as_strided(y, shape=shape, strides=strides)
        return np.sqrt(np.mean(frames**2, axis=1))
    except Exception as e:
        log.error("Error during RMS striding: %s", e)
        return np.array([])


# ---------- core algo --------------------------------------


async def extract(audio_path: str) -> AudioPerception:
    """Async entry-point; CPU work offloaded to thread."""
    loop = asyncio.get_running_loop()
    # Use default ThreadPoolExecutor; consider ProcessPoolExecutor for heavy CPU loads
    return await loop.run_in_executor(None, extract_sync, audio_path)


def extract_sync(path: str) -> AudioPerception:
    """Synchronous implementation of audio feature extraction."""
    try:
        y, sr = sf.read(path)
    except sf.SoundFileError as e:
        log.error("Failed to read audio file %s: %s", path, e)
        raise

    # Handle stereo audio (downmix to mono)
    if y.ndim > 1:
        y = np.mean(y, axis=1)

    # Normalize audio data to float32 [-1.0, 1.0]
    if y.dtype != np.float32:
        original_dtype = y.dtype
        y = y.astype(np.float32)

        if np.max(np.abs(y)) > 1.0:
            if original_dtype == np.int16:
                y /= 32768.0
            elif original_dtype == np.int32:
                y /= 2147483648.0
            elif original_dtype == np.uint8:
                y = (y - 128.0) / 128.0

    y = np.clip(y, -1.0, 1.0)

    # --- Parameter Calculation ------------------------------
    win_samp, hop_samp = int(WINDOW_SEC * sr), int(HOP_SEC * sr)

    if win_samp == 0 or hop_samp == 0:
        raise ValueError(f"Window/hop size zero. Check sample rate ({sr}) and config.")

    # --- Silence and Pacing (RMS) ---------------------------
    rms = _rms_energy(y, win_samp, hop_samp)

    if rms.size == 0:
        log.warning("Audio file too short for analysis: %s", path)
        return AudioPerception(silence_segments=[], pacing_curve=[], rhythm_onsets=[])

    pacing_curve = rms.tolist()

    # Silence detection
    thresh = _db2amp(SILENCE_THRESHOLD_DB)
    silent = rms < thresh
    silent_indices = np.where(silent)[0]
    silent_s = silent_indices * HOP_SEC

    silence_segments: list[tuple[float, float]] = []
    if silent_s.size:
        # Find breaks in continuous silence using index differences
        breaks = np.where(np.diff(silent_indices) > 1)[0] + 1
        breaks = np.concatenate(([0], breaks, [silent_s.size]))
        for i in range(len(breaks) - 1):
            start_idx = breaks[i]
            end_idx = breaks[i + 1] - 1
            start = silent_s[start_idx]
            # The end time is the end of the last silent frame
            end = silent_s[end_idx] + HOP_SEC
            if end - start >= MIN_SILENCE_SEC:
                silence_segments.append((round(start, 3), round(end, 3)))

    # --- Rhythm (Onsets via STFT novelty) -------------------
    noverlap = max(0, win_samp - hop_samp)

    _, times, spectrum = scipy_stft(y, fs=sr, nperseg=win_samp, noverlap=noverlap)

    # Calculate onset strength (Spectral Flux)
    if spectrum.shape[1] > 1:
        onset_env = np.linalg.norm(np.diff(np.abs(spectrum), axis=1), axis=0)
        if onset_env.max() > 0:
            onset_env = onset_env / onset_env.max()  # Normalize

        # Find peaks
        min_distance = max(1, int(0.1 * sr / hop_samp))  # Min distance 100ms
        peaks, _ = find_peaks(onset_env, height=ONSET_THRESHOLD, distance=min_distance)

        # Convert peak indices to time (offset by 1 due to diff)
        rhythm_onsets = times[peaks + 1].tolist()
    else:
        rhythm_onsets = []

    return AudioPerception(
        silence_segments=silence_segments,
        pacing_curve=pacing_curve,
        rhythm_onsets=[round(r, 3) for r in rhythm_onsets],
    )
