# AutoCutAI

Autonomous video-editing primitives for semiotic and rhythmic rough cuts.

> **Status:** early-stage research scaffold. Today this repository implements a single, well-tested rough-cut policy (beat-aligned shot assembly) plus a chaos-analysis CI surface. The broader vision — semiotic parsing, affective curve extraction, generative edit grammar — is *design intent* and lives in [`DESIGN.md`](DESIGN.md), not in this README.

If you came here expecting "drop raw clips, get a finished reel," please read `DESIGN.md` first. That is the destination, not the current behaviour.

---

## What works today

### Editor — `editor.v1` (SimpleBeatSyncPolicy)

A deterministic, frame-accurate rough-cut policy:

- Takes a `VideoStructurePerception` (shot boundaries, fps, resolution) and an `AudioPerception` (onset frames).
- Drops shots shorter than `MIN_SHOT_DURATION_SEC` (0.5 s).
- Aligns each surviving shot's start frame to the nearest beat at or after the original start.
- Re-validates duration after alignment; drops slivers.
- Emits a `RoughCut` of `EditDecision`s with inclusive `[src_in, src_out]` ranges and a destination cursor.
- Refuses frame-rate conversion (forces `output_fps == video_perception.fps`).
- Exports a CSV EDL via `RoughCut.to_csv(path)`.

Source: `src/autocutai/editor/v1.py`, `src/autocutai/editor/contract.py`.
Tests: `tests/editor/test_editor_v1.py`.

### Perception primitives

- `autocutai.perception.audio` — onset extraction.
- `autocutai.perception.video` — shot-boundary structure.

### Native chaos-analysis tools

Three C++ helpers compile from this repository:

- `wtmm` — WTMM multifractal-width estimator (GSL).
- `bb-extract` — basic-block hit-matrix exporter from `llvm-cov` JSON (nlohmann-json).
- `jnorm` — interval-arithmetic Jacobian ∞-norm over LLVM IR (LLVM 15).

Build with `make native-tools`. See [`docs/ci-and-native-tools.md`](docs/ci-and-native-tools.md).

These tools currently operate on placeholder targets in CI. The chaos-check workflow is a structural smoke test, not a formal-verification guarantee — see the "Chaos-check pipeline — scaffolding, not proof" section of `DESIGN.md` for the full caveats.

---

## Install

Requires Python 3.12 or 3.13 and [Poetry](https://python-poetry.org/) 2.4.1.

```sh
poetry install
poetry run pytest
```

To build the native chaos tools you additionally need `g++`, GSL, nlohmann-json, and LLVM 15:

```sh
make native-tools
```

---

## Quickstart — beat-aligned rough cut

```python
from autocutai.editor.v1 import rough_cut_v1
from autocutai.perception.audio import AudioPerception
from autocutai.perception.video import VideoStructurePerception

video = VideoStructurePerception.from_file("input.mp4")
audio = AudioPerception.from_file("input.mp4")

edl = rough_cut_v1(video, audio, source_file="input.mp4")
edl.to_csv("rough_cut.csv")
```

The output is an EDL, not a rendered video. Rendering from the EDL is a separate step (see `src/autocutai/editor/render.py`).

---

## CI

Two workflows run on every push and pull request:

- `ci.yml` — `poetry check --lock`, install, `black --check`, `ruff check`, `mypy`, `pytest` on Python 3.12 and 3.13.
- `chaos-check.yml` — builds the native tools and runs `ci/0-setup.sh` through `ci/10-seal.sh`. See `DESIGN.md` for what this pipeline does and does not currently prove.

---

## Project layout

```
src/autocutai/
  editor/         # rough-cut policies + EDL contract
  perception/     # audio onsets, video shot structure
  math/           # shared math utilities

ci/               # chaos-analysis pipeline (shell + python)
fixtures/chaos/   # committed inputs for the chaos pipeline
tests/            # pytest suite
wtmm.cpp jnorm.cpp bb-extract.cpp   # native tool sources
```

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). For where the project is headed and which areas are open for research, see [`DESIGN.md`](DESIGN.md).

## License

Apache 2.0 — see [`LICENSE`](LICENSE).
