# 02: Resilient Metadata Fallback Parsing

**What to build:**
Ensure Release extraction seamlessly falls back to OpenGraph and page-title metadata without throwing AttributeError crashes on delimiter splitting, ensuring that non-standard Bandcamp release pages are safely ingested as Degraded Releases rather than breaking the sync job.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] Delimiter splitting on fallback title/artist correctly references parts[1].strip() instead of calling .strip() on list.
- [x] Fallback extraction handles ', by ', ' - ', ' by ', and ' | ' gracefully.
- [x] Variable naming is cleaned up (	_data renamed to 	ralbum_data).
