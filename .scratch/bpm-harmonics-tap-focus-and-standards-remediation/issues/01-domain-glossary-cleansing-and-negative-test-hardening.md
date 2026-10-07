# 01: Domain Glossary Cleansing and Negative Test Hardening

**What to build:**
Thoroughly eliminate all remaining forbidden terms defined in `CONTEXT.md` from the frontend templates and establish strict negative regression assertions in the test suite. Specifically, replace `ITEM: ${selectedIndex + 1}` with `RELEASE: ${selectedIndex + 1}` in keyboard navigation HUD notices, replace `搜尋藝人、專輯` with `搜尋藝人、作品` in search placeholder text, and rename `drawer-album-title` to `drawer-release-title`. Add explicit `assertNotIn` checks in `tests/test_ui_refinements.py` for each forbidden phrase to permanently prevent regressions.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] `triggerHUD` notices for card navigation in `app/templates/index.html` use canonical term `RELEASE: ${selectedIndex + 1}/${flatCards.length}` instead of `ITEM:`
- [x] Search input placeholder in `app/templates/index.html` prompts for `搜尋藝人、作品 (Esc 清除)...` instead of using forbidden term `專輯`
- [x] Multi-track drawer header element in `app/templates/index.html` and its JavaScript references use `id="drawer-release-title"` instead of `drawer-album-title`
- [x] `tests/test_ui_refinements.py` includes negative assertions verifying that `ITEM:`, `搜尋藝人、專輯`, and `drawer-album-title` do not exist in `html_content`
- [x] Duplicated assertions in `tests/test_ui_refinements.py` are cleaned up
