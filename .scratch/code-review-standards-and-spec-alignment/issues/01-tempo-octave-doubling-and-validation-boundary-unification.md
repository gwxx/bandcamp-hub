# 01: Tempo Octave Doubling and Validation Boundary Unification

**What to build:**
Expand the client-side Web Audio autocorrelation analyzer's octave doubling normalization to 60 ~ 180 BPM, accurately preserving downtempo/ambient tracks (60–69 BPM) and fast drum & bass/jungle tracks (166–180 BPM). Synchronize input validation across both frontend and backend strictly to the range of 40.0 to 300.0 BPM, closing the sub-1.0 validation loophole in the backend API.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] Web Audio BPM analyzer in `index.html` normalizes tempos via `while (bpm < 60) bpm *= 2; while (bpm > 180) bpm /= 2;`
- [x] Backend endpoint `PATCH /api/releases/{release_id}/bpm` validates `40.0 <= payload.bpm <= 300.0` and raises HTTP 400 for values outside this range
- [x] Frontend manual BPM input and nudge handlers validate `40.0 <= bpm <= 300.0`
- [x] Backend tests in `test_audio_resilience_and_bpm.py` and `test_bpm_analyzer_and_proxy.py` cover boundary values (e.g. 39.9 rejected, 40.0 accepted, 300.0 accepted, 300.1 rejected)
