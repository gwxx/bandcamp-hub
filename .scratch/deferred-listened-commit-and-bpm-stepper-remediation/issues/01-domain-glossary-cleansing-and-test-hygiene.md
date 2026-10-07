# 01: Domain Glossary Cleansing and Test Hygiene

**What to build:**
Eradicate all remaining instances of the forbidden domain term "專輯" (Album) from code comments across the template, replacing them with canonical domain vocabulary ("發行" / "Release"). Refactor the UI refinement test suite by hoisting repeated `import re` statements to module level, eliminating duplicate 70–200 BPM loop assertions, and adding a strict global negative assertion ensuring "專輯" never appears anywhere in rendered template HTML.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] All 5 comment occurrences of "專輯" in `app/templates/index.html` (L1592, L1603, L1637, L1648, L1912) are replaced with "發行"
- [x] `tests/test_ui_refinements.py` hoists `import re` to the top of the file and removes duplicate inline imports
- [x] Duplicate BPM normalization loop assertions (`while (bpm < 70)...` & `while (bpm > 200)...`) are removed from `test_bpm_normalization_and_state_machine_templates`
- [x] `tests/test_ui_refinements.py` enforces global negative assertion `self.assertNotIn("專輯", self.html_content)`
- [x] All tests in `tests/test_ui_refinements.py` pass cleanly
