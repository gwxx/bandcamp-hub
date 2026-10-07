# 04: Domain Glossary Harmonization across UI, HUD, and Tests

**What to build:**
Harmonize user interface copy, heads-up display notices, and test fixture definitions to strictly comply with `CONTEXT.md`. Replace all UI occurrences of the forbidden synonym "歌曲" with standard "曲目" (Track), change the bulk-listened HUD notification to "WEEK {week}: LISTENED", and update test fixtures from "Test Album" to "Test Release".

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] All instances of "歌曲" in `app/templates/index.html` updated to "曲目" (Track)
- [x] Heads-up display (HUD) feedback in `markWeekAllListened` emits `WEEK ${weekStr}: LISTENED`
- [x] Test fixtures across `tests/` replace `'Test Album'` and `'Empty Album'` with `'Test Release'` and `'Empty Release'`
- [x] Complete test suite passes with 100% adherence to domain definitions
