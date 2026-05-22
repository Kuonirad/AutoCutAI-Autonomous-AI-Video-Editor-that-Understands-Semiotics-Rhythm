# AutoCutAI — Design & Roadmap

This document captures the **research direction** for AutoCutAI and is intentionally distinct from `README.md`, which describes only what currently runs. Everything below should be read as *aspirational architecture* and *open research*, not as implemented behaviour.

If a section here is not also reflected in `src/autocutai/` and exercised by tests, treat it as roadmap.

---

## Vision

AutoCutAI aims to be an autonomous video editor that operates not by snapping cuts to transients, but by *interpreting* the meaning of shots, pacing, and audiovisual emotion. The framing is that video is a **language** and editing is **generative grammar** over that language.

This is the long-term target. The codebase today implements the first, simplest layer of this stack (beat-aligned rough cuts); the rest is design intent.

### What "understanding" is meant to mean

| Human editor intuition | AutoCutAI equivalent (target) |
|------------------------|-------------------------------|
| "This shot drags."     | Arousal-decay curve — detect when engagement drops below threshold via facial micro-expressions + audio valence. |
| "Cut on the downbeat, but late by 200 ms to create tension." | Rhythmic-semiotics model — learn that *delay* encodes *tension* in genre-specific contexts. |
| "This grade feels hopeful." | Color-semiotics vector — map hue/saturation clusters to emotional valence in a latent space trained on film-theory datasets. |
| "This clip is diegetically disconnected." | Diegetic-coherence graph — check that audio-reverb signatures, lighting direction, and eyeline vectors align across cuts. |

---

## Target architecture (not yet implemented)

```python
# Pseudo-pipeline. None of these modules exist yet in src/autocutai/.
clips = load_clips()

# 1. Semiotic parsing
semiotic_graph = SemioticParser(clips)         # nodes = shots, edges = meaning-relations

# 2. Affective curve extraction
arousal = MultimodalArousalModel(clips)        # facial AU + audio spectral centroid + color energy

# 3. Rhythmic structure induction
rhythm = RhythmInducer(clips)                  # beat, micro-rhythm, breathing patterns

# 4. Generative edit grammar
edit_sequence = SemioticGrammar.sample(
    semiotics=semiotic_graph,
    arousal=arousal,
    rhythm=rhythm,
    genre=genre_prompt                         # e.g., "cinematic trailer, slow-burn horror"
)

# 5. Render
final_timeline = EditRenderer(edit_sequence, clips)
```

What exists today corresponds to a degenerate special case of step 3 (beat onsets) plus a minimal step 5 (frame-accurate EDL). Steps 1, 2, and 4 are open work.

### How semiotics would be learned

1. **Dataset**: ~10 000 professionally edited videos, annotated with per-frame valence/arousal, cut type (J-cut, L-cut, match cut, jump cut, …), color-script tags, and diegetic / non-diegetic audio labels.
2. **Training signal**: next-cut prediction conditioned on a partial timeline — forces the model to internalise *why* cuts happen, not just *where*.
3. **Loss**:
   ```
   L = L_cut_accuracy + λ₁ · L_emotion_curve_match + λ₂ · L_semiotic_coherence
   ```

None of this dataset or training code exists in this repository.

### Intended end-user experience

| Input | Target output |
|-------|---------------|
| 45 min of raw travel footage + prompt "make me feel wanderlust" | ~60 s reel with breathing pacing, color-warmth ramp, music that swells on a smile, cuts timed to *footsteps* rather than beats. |
| 20 min interview + B-roll + prompt "corporate hype, but human" | ~90 s piece with micro-pauses on emotional words, B-roll on cognitive-load drops, color temp cools during stats and warms during anecdotes. |

### Differentiation from beat-snap editors (target)

| Feature | AutoCutAI (target) | Beat-based cutters |
|---------|--------------------|--------------------|
| Cuts on | Meaning transitions | Transients |
| Timing | Emotional cadence | BPM grid |
| Color | Semiotic valence | LUT template |
| Audio | Diegetic continuity | Waveform snap |

### Known hard problems

- **Compute**: a full semiotic parse is expected to scale O(n²) in shot count; this number is a design estimate, not measured.
- **Fidelity**: the long-term target is roughly 85 % of human-editor intent. Ironic and meta narratives (parody, satire) are expected to remain hard.
- **Data hunger**: annotated emotional curves are expensive to source at scale.
- **Cross-cultural semiotics**: a cut that reads as *triumphant* in one culture can read as *rushed* in another. Per-culture latent spaces with learned transfer functions are an open direction.

---

## Chaos-check pipeline — scaffolding, not proof

The `ci/` directory and the `chaos-check` workflow are an early experiment in subjecting the project's *own* behaviour to formal and information-theoretic checks: Intel-PT-style traces, attractor embedding, WTMM multifractal width, PCMCI causal discovery, CBMC bounded model checking, a Jacobian-norm contraction check, an entropy-budget step, and a final SHA-512 seal.

The framing is intentional. The current implementation is **not**.

### What is real today

- The three native helpers (`wtmm`, `bb-extract`, `jnorm`) compile and run.
- `wtmm.cpp` computes a WTMM-based multifractal width on a real input signal.
- `bb-extract.cpp` reads `llvm-cov` JSON and emits a basic-block hit matrix.
- `jnorm.cpp` performs an interval-arithmetic walk over LLVM IR for `FAdd`/`FSub`/`FMul`. PHI nodes and most other opcodes fall through to the worst-case interval `[-∞, +∞]`, and the traversal is unbounded recursion without memoisation — fine on toy inputs, not yet production-grade.
- Pipeline outputs are hashed at the end (`ci/10-seal.sh`).

### What is currently placeholder

- **`target.c` and `target_patched.c` are `Hello, world!` stubs**, and `target.patch` is a comment, not a diff. Anything CBMC and `jnorm` "verify" today is verifying these stubs, not editor logic.
- **`ci/5-cbmc.sh` falls back to writing `VERIFICATION SUCCESSFUL` to `cbmc.out` when CBMC is not installed** on the runner, and the subsequent `grep` then passes the gate. On a standard GitHub-hosted runner without CBMC, the bounded-model-check step is effectively a no-op that returns green. This is convenient for keeping the workflow exercised, but it means a green `chaos-check` badge does **not** currently constitute a model-checking guarantee.
- **`ci/9-entropy.sh` exits 0 even on `ENTROPY_WARN`** — the entropy budget is informational, not a gate.
- **`ci/1-trace.sh`** falls back to a deterministic synthetic trace when Intel PT is unavailable; this is honest about its provenance but should not be read as real branch data.
- The AWS QLDB seal in `ci/10-seal.sh` runs only when credentials are present; otherwise the local `SHA512SUMS` file is the seal.

### What the chaos-check pipeline therefore *is*, today

A structural smoke test that:

1. Confirms the native toolchain builds and runs end-to-end.
2. Produces deterministic artefacts that can be diffed across commits.
3. Establishes the *shape* of a verification pipeline that future work can fill in with real targets and a real CBMC step.

It is **not**, today:

- A proof that any production code is free of the behaviours CBMC could rule out.
- A proof that a patch is contractive in any meaningful sense (the contraction check runs against the patched `Hello, world!`).
- An entropy gate on real editor behaviour.

### Path to making it real

In rough priority order:

1. Replace `target.c` / `target_patched.c` with an actual minimal slice of editor logic compiled to C (or expose a C-shaped harness around a chosen invariant of `rough_cut_v1`).
2. Make `ci/5-cbmc.sh` **fail** when CBMC is unavailable, or move the fallback behind an explicit `CHAOS_ALLOW_NO_CBMC=1` flag so the default is honest.
3. Promote `ci/9-entropy.sh` to a real gate once it runs against real test output instead of placeholder `tests/*.out`.
4. Add memoisation and PHI-node handling to `jnorm.cpp` before relying on its norm for anything non-trivial.
5. Pin native-toolchain versions (LLVM, GSL, nlohmann-json) via a container so the multifractal / interval-arithmetic results are reproducible across hosts.

Until those land, the right mental model is: *the chaos-check pipeline is scaffolding for a verification practice we want to have, not evidence that we already have it.*

---

## Status summary

| Area | Status |
|------|--------|
| `editor.v1` beat-aligned rough cut | Implemented, tested |
| `EditDecision` / `RoughCut` contract + CSV export | Implemented |
| Audio onset perception | Implemented (`perception/audio/v1.py`) |
| Video shot perception | Implemented (`perception/video/`) |
| Semiotic parser | Not started |
| Affective / arousal model | Not started |
| Rhythm inducer (beyond onsets) | Not started |
| Generative edit grammar | Not started |
| Cross-cultural semiotics | Research direction only |
| Chaos-check pipeline | Scaffolding; see section above |
| Hermetic container (Docker / devcontainer) | Not yet present |
| SHA-pinned GitHub Actions + explicit `permissions:` | Not yet applied |

When a row moves from "not started" to "implemented", it should also be removed from the *aspirational* sections above and described in `README.md`.
