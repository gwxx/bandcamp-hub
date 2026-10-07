# 02: Tap Tempo Focus Lock and Input Defense

**What to build:**
Lock keyboard focus to `#btn-tap-tempo` upon opening manual edit mode and during tap tempo execution, and install defensive keyboard event handling on `#custom-bpm-input`. If a user types into the custom BPM input field and presses physical `T/t`, the listener intercepts the event, releases text input focus (`blur()`), locks focus to `#btn-tap-tempo`, and directly invokes `handleTapTempo()`, ensuring uninterrupted tempo tapping regardless of prior input interaction.

**Blocked by:** 01-domain-glossary-cleansing-and-test-hygiene

**Status:** resolved

- [x] `toggleBpmEditMode()` explicitly transfers focus to `document.getElementById('btn-tap-tempo')` when expanding edit mode
- [x] `handleTapTempo()` explicitly maintains focus on `document.getElementById('btn-tap-tempo')` upon each tap
- [x] `#custom-bpm-input` listens for `keydown` events; pressing `T` or `t` calls `e.preventDefault()`, blurs the input element, sets focus to `#btn-tap-tempo`, and triggers `handleTapTempo()`
- [x] Automated regression tests in `tests/test_ui_refinements.py` assert presence of focus locks and input keydown interception
- [x] All tests in `tests/test_ui_refinements.py` pass cleanly
