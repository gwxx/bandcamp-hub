# 0004. One-Way Promotion Curation State Machine

User interaction transitions follow a one-way promotion model: marking a Release as Starred automatically sets its status to Listened (`is_listened = 1`), but unstarring or resetting Listened state preserves the independent user intent.

## Context
During weekly music curation (Inbox Zero workflow), users audit incoming releases. A user who favorites a release has undoubtedly evaluated it, making requiring a separate "Mark as Listened" click redundant. However, reverting a favorite or re-flagging a track for re-listening involves subtle psychological distinctions in music curation.

## Decision
We implemented asymmetric state machine transitions:
1. **Starring (`is_starred: 0 -> 1`)**: Implicitly promotes `is_listened = 1` and dismisses the release from the Unlistened view.
2. **Unstarring (`is_starred: 1 -> 0`)**: Retains `is_listened = 1` (the user still listened to and evaluated the release).
3. **Marking as Unlistened (`is_listened: 1 -> 0`)**: Retains `is_starred = 1` (allows keeping a favorite while queuing it for another listen).

## Consequences
- Reduces interaction friction by 50% for favorable discoveries during high-speed triage.
- Prevents unintended state erasure when users adjust favorites or mark items for re-listening.
