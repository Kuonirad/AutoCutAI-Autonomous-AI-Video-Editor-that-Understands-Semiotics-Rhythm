"""
Tests for autocutai.perception.audio.v1
"""

from collections.abc import Generator
import os
import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from autocutai.perception.audio import AudioPerception, extract, extract_sync


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------
@pytest.fixture(scope="module", params=[8000, 16000, 22050, 44100])
def sr(request):
    """Sample rates to exercise."""
    return request.param


@pytest.fixture(scope="module", params=["float32", "int16"])
def dtype(request):
    """PCM formats."""
    return request.param


@pytest.fixture
def silent_then_tone_wav(sr: int, dtype: str) -> Generator[Path, None, None]:
    """5-second file: 1 s tone, 1 s silence, 2 s tone, 1 s silence."""
    duration = 5.0
    tone_freq = 440.0
    t = np.linspace(0, duration, int(sr * duration))
    y = np.zeros_like(t)

    # 0-1 s tone
    y[:sr] = 0.5 * np.sin(2 * np.pi * tone_freq * t[:sr])
    # 2-4 s tone
    y[2 * sr : 4 * sr] = 0.5 * np.sin(2 * np.pi * tone_freq * t[2 * sr : 4 * sr])
    # rest is zero (silence)

    if dtype == "int16":
        y = (y * 32767).astype(np.int16)
    else:
        y = y.astype(np.float32)

    fd, fname = tempfile.mkstemp(suffix=".wav")
    sf.write(fname, y, sr)
    os.close(fd)
    yield Path(fname)
    Path(fname).unlink()


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------
@pytest.mark.asyncio
async def test_extract_smoke(silent_then_tone_wav: Path):
    """Happy path: returns expected dataclass and finds silence."""
    perception: AudioPerception = await extract(str(silent_then_tone_wav))

    assert isinstance(perception, AudioPerception)
    assert len(perception.silence_segments) >= 1
    # at least one silence gap ~1 s between 1-2 s
    gap = next((s, e) for s, e in perception.silence_segments if 1.0 <= s <= 1.2)
    assert gap[1] - gap[0] == pytest.approx(1.0, abs=0.1)

    assert len(perception.pacing_curve) > 0
    assert len(perception.rhythm_onsets) >= 3  # onsets at start of each tone burst


@pytest.mark.asyncio
async def test_extract_mono_stereo(sr: int):
    """Ensure stereo files are handled (sum-to-mono internally)."""
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration))
    y = np.column_stack([np.sin(2 * np.pi * 440 * t)] * 2)  # stereo
    fd, fname = tempfile.mkstemp(suffix=".wav")
    sf.write(fname, y, sr)
    os.close(fd)

    perception: AudioPerception = await extract(str(fname))
    Path(fname).unlink()
    assert len(perception.pacing_curve) > 0


@pytest.mark.asyncio
async def test_extract_tiny_file(sr: int):
    """Edge case: 50 ms file should not crash."""
    y = np.random.randn(int(sr * 0.05)).astype(np.float32)
    fd, fname = tempfile.mkstemp(suffix=".wav")
    sf.write(fname, y, sr)
    os.close(fd)

    perception: AudioPerception = await extract(str(fname))
    Path(fname).unlink()
    # simply not exploding is success
    assert isinstance(perception, AudioPerception)


@pytest.mark.asyncio
async def test_extract_file_not_found():
    """Ensure a clear error is raised for missing files."""
    with pytest.raises(sf.SoundFileError):
        await extract("non_existent_file.wav")


def test_extract_sync_low_samplerate_raises_error():
    """A sample rate that causes window/hop to be zero should raise ValueError."""
    # Create a dummy file with a low sample rate
    sr = 10  # Below the threshold to make window/hop zero
    y = np.zeros(sr * 1)  # 1 second of audio
    fd, fname = tempfile.mkstemp(suffix=".wav")
    sf.write(fname, y.astype(np.float32), sr)
    os.close(fd)

    with pytest.raises(ValueError, match="Window/hop size zero"):
        extract_sync(str(fname))

    Path(fname).unlink()
