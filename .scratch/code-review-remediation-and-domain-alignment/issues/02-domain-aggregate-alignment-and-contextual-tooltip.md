# 02: Domain Aggregate Alignment and Contextual Tooltip Refinement

**What to build:**
Reconcile the interaction between playing individual tracks and cataloging Release-level metadata. Refine the BPM analysis button copy to "分析目前播放曲目 BPM" (or "重新分析目前播放曲目 BPM") and provide a clear tooltip stating that the analyzed tempo serves as the base BPM for the active Release aggregate, preserving domain integrity according to `CONTEXT.md`.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] Analysis button text dynamically toggles between "🔍 分析目前播放曲目 BPM" (when no BPM is saved) and "🔄 重新分析目前播放曲目 BPM" (when a persisted BPM exists)
- [x] Button `title` attribute communicates that the BPM will be assigned to the active Release aggregate: "此 BPM 將作為此 Release 之基準節奏"
- [x] UI labels maintain 100% adherence to `CONTEXT.md` (no forbidden synonyms, strict separation of Track playback and Release persistence)
