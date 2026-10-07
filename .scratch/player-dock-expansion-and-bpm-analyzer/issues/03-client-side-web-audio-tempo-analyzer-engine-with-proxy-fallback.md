# 03: Client-Side Web Audio Tempo Analyzer Engine with Proxy Fallback

**What to build:**
Implement an automated, client-side tempo detection engine using the browser's Web Audio API (`AudioContext` / `OfflineAudioContext`). It decodes audio samples from the active Track preview stream, isolates kick and rhythm transient frequencies via a low-pass biquad filter (~150Hz), and calculates peak intervals/autocorrelation to estimate BPM within 1-2 seconds. Provide a lightweight backend audio streaming proxy endpoint (`GET /api/releases/{release_id}/stream-proxy`) as a fallback to guarantee 100% CORS-free decoding across all CDN environments.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] Backend provides `GET /api/releases/{release_id}/stream-proxy` with range request and streaming response support
- [x] Backend test covers the stream proxy endpoint under `tests/test_bpm_analyzer_and_proxy.py`
- [x] Client Web Audio analyzer decodes audio buffer from direct stream or proxy fallback
- [x] Low-pass filter and peak energy autocorrelation algorithm calculates tempo in BPM (bounded between 60 and 190 BPM)
- [x] Analysis executes asynchronously without blocking the browser UI or active audio playback
