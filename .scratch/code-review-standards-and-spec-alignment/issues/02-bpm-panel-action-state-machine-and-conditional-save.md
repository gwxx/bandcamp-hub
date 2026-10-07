# 02: BPM Panel Action State Machine and Conditional Save Trigger

**What to build:**
Deliver the dynamic action state machine inside the DJ BPM panel. When an active Track already has a persisted base BPM, the button indicates "🔄 重新分析目前曲目 BPM"; if no BPM is saved, it indicates "🔍 自動分析目前曲目 BPM". During active analysis, display "⚡ 分析中..." with a pulsing visual animation (`animate-pulse`). Dynamically reveal the "✓ 確認儲存至資料庫" button only when the staged BPM is unsaved or modified, hiding it when the value matches the database.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] Analysis button text dynamically toggles between "🔍 自動分析目前曲目 BPM" (no saved BPM) and "🔄 重新分析目前曲目 BPM" (existing BPM)
- [x] During analysis, button disables, icon shows "⚡", and text shows "分析中..." with Tailwind `animate-pulse` class
- [x] Save button `#btn-save-staged-bpm` appears only when `stagedBpm` differs from `activeRelease.bpm` (or when `activeRelease.bpm` is unset), and hides when saved
- [x] Mini player capsule badge maintains subtle asterisk badge (`${effBpm}* BPM`) when staged adjustments remain unpersisted
