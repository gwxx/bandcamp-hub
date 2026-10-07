# Spec: Player Dock Ergonomics Expansion and Smart BPM Analysis

Status: ready-for-agent

## Problem Statement

Curators and DJs using Bandcamp Hub encounter spatial cramping and workflow friction in the floating vinyl capsule player:

1. **Boundary Clipping on Rightmost Icons**: In the floating capsule player, the outer pill wrapper's circular corner radius encroaches on the rightmost utility controls. The external Bandcamp icon touches or exceeds the visual boundary of the pill, creating an unpolished aesthetic and poor touch/click ergonomics.
2. **Undersized Icon Targets**: Action icons across the player (transport controls, volume, shuffle, loop, star, listened) remain sized at standard micro dimensions (`16px`), causing mis-clicks and requiring excessive visual focus during high-speed music auditing.
3. **Cumbersome BPM Workflow**: The existing DJ tempo controller relies on the user to manually estimate or independently look up BPM before typing it into a raw input field. Users lack an automated way to detect the tempo of the currently auditioned Track directly within the hub.
4. **Rigid BPM Fine-Tuning**: Once a BPM is determined, users cannot rapidly nudge the tempo by standard DJ intervals (e.g. ±2 BPM) without typing, and lack a staged review process that lets them audit and adjust the detected value before permanently persisting it to the Evergreen Vault.

## Solution

Deliver a spacious, ergonomically refined floating player capsule with an integrated client-side Smart BPM Analyzer:

1. **Wide Capsule Geometry**: Expand the player capsule maximum width to `1280px` (`max-w-7xl`) and enlarge side margins to `32px` (`px-8`), ensuring ample breathing room between the curved pill caps and the outer utility icons.
2. **Comfort-Scaled Iconography**: Elevate all player transport and utility icons to `20px` (`w-5 h-5`) and scale the primary play/pause button to `44px` (`w-11 h-11`), creating generous click hitboxes and crisp visual hierarchy.
3. **Integrated Audio Tempo Analyzer**: Add a one-click automated tempo detection engine within the DJ Tempo popover panel that analyzes the currently playing Track's audio waveform via the browser's Web Audio API, extracting rhythmic kick and peak energy patterns to compute tempo in seconds without server load.
4. **Staged BPM Review and Nudge Workflow**: Present the detected BPM in a staging state with rapid `+2` and `-2` BPM nudge buttons, an inline `Edit` toggle for precise manual numeric overrides, and an explicit `Save` action that commits the validated tempo to the Evergreen Vault.
5. **Preserved Master Tempo Pitch Shifting**: Retain native pitch preservation (`preservesPitch = true`) and continuous playback speed adjustment (`0.80x ~ 1.20x`) so DJs can audition tracks across tempo ranges without key distortion.

## User Stories

1. As a music curator on a standard or wide desktop screen, I want the player dock to have a generous width of up to 1280px, so that controls never feel congested or cramped.
2. As a music curator, I want the rightmost Bandcamp external link icon to sit comfortably inside the curved capsule boundary with ample padding, so that it is never clipped or overflowing the dock edge.
3. As a listener, I want larger 20px action icons for playback controls, volume, star, and listened toggles, so that I can click them effortlessly without straining my eyes or precision.
4. As a DJ reviewing an unfamiliar Release, I want to click a single "Analyze BPM" button to automatically detect the Track's tempo, so that I don't have to switch to external tempo calculation tools.
5. As a DJ, I want tempo analysis to execute directly in my browser using client-side Web Audio processing, so that results appear within seconds without sending heavy audio payloads to the server.
6. As a DJ evaluating an analyzed tempo, I want to see the detected BPM displayed in a temporary review state, so that I can audit its accuracy before writing to my Evergreen Vault.
7. As a DJ, I want quick "+2" and "-2" adjustment buttons next to the detected BPM, so that I can easily nudge the base tempo up or down by two beats per minute.
8. As a DJ encountering a half-time or fractional detection, I want an "Edit" button that reveals an inline numeric input field, so that I can manually type the exact integer or decimal BPM.
9. As a music curator, I want an explicit "Save" button to commit the confirmed BPM to the database, so that accidental detections or unverified values are not persisted automatically.
10. As a DJ preparing a mix, I want adjusting the playback speed slider between 0.8x and 1.2x to dynamically recalculate the effective BPM while keeping musical pitch unaltered, so that I can hear how a Track feels at higher or lower tempos.
11. As a user operating across multiple tracks, I want switching to another Track or Release to smoothly reset the analyzer interface while retaining previously persisted BPMs for already-analyzed works.

## Implementation Decisions

### 1. Dock Architecture and Responsive Layout
- Scale the `#player-dock` maximum width constraint to `max-w-7xl` (`1280px`), maintaining fluid responsive width (`w-[calc(100%-2rem)]`) on narrower viewports.
- Enforce deep horizontal padding (`px-8 py-3`) on the inner `.glass-panel` capsule to insulate icons from the `rounded-full` border radius curvature.
- Upgrade SVG icon viewports and classes from `w-4 h-4` to `w-5 h-5` across previous, next, shuffle, loop, volume, star, listened, and Bandcamp external link elements.
- Increase the central play/pause trigger to `w-11 h-11` (44px) with scaled typography.

### 2. Client-Side Web Audio BPM Analyzer
- Utilize the browser's native `AudioContext` and `OfflineAudioContext` to decode an audio sample buffer (first 30-60 seconds of the active Track preview stream).
- Apply a Biquad low-pass filter (cutoff around 150Hz) to isolate kick drum transients and rhythmic downbeats.
- Perform peak energy thresholding and autocorrelation across time intervals to derive the dominant tempo between 60 BPM and 180 BPM.
- Provide a backend audio streaming proxy endpoint if direct cross-origin media buffer fetching is blocked by CDN headers, guaranteeing 100% reliable decoding.

### 3. Staged BPM Interactive State Machine
- When the DJ Tempo popover opens:
  - If a base BPM is already saved in the Release record: display the persisted base BPM alongside the "Edit" and "Re-analyze" options.
  - If no base BPM exists: surface the prominent "🔍 自動分析目前歌曲 BPM" action button.
- Analysis State: Disable the trigger, display a pulse indicator (`⚡ 分析中...`), and compute tempo asynchronously.
- Staged Review State:
  - Render detected tempo badge (e.g. `124.0 BPM`).
  - Render immediate `[-2]` and `[+2]` nudge buttons to step the staged value by 2.0 BPM.
  - Render `[✏️ Edit]` toggle to expose a direct numeric input field for custom manual entry.
  - Render `[確認儲存]` (Save) button to commit the value to the database via `PATCH /api/releases/{release_id}/bpm`.
- Post-Save State: Update the mini player capsule badge, reflect the saved value across open UI views, and trigger a non-blocking confirmation HUD toast.

### 4. Preservation of Real-Time Pitch Shifting
- Maintain HTML5 `audio.playbackRate = currentPitch` paired with `audio.preservesPitch = true`.
- Slider range remains bounded to `0.80x ~ 1.20x` with fine `±1%` nudge buttons.
- Effective tempo continuously recalculates dynamically: $\text{Effective BPM} = \text{Base BPM} \times \text{Current Pitch}$.

## Testing Decisions

- **Automated API Integration Tests**: Verify that `PATCH /api/releases/{release_id}/bpm` continues to safely accept, validate, and persist both integer and floating-point BPM values (between 1.0 and 300.0) and correctly rejects out-of-range payloads.
- **Audio Proxy Resilience Tests**: Test that the audio proxy endpoint correctly streams audio bytes with appropriate MIME headers and range-request compatibility.
- **Client End-to-End Ergonomics Verification**: Verify in the browser that dock elements do not wrap, the rightmost icon preserves at least 16px clearance from the curved capsule edge, and the BPM popover transitions seamlessly through Analyze $\rightarrow$ Nudge/Edit $\rightarrow$ Save states.

## Out of Scope

- Cloud-based artificial intelligence stem separation or musical key detection (Camelot key / harmonic mixing tags).
- Persistent multi-cue point memory markers saved across browser sessions.
- Audio waveform visualizer scrubbers inside the mini player dock.

## Further Notes

- The Web Audio API analysis executes entirely inside worker buffers or offline rendering contexts, creating negligible CPU overhead during live audio playback.
