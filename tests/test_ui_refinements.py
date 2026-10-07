import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import re
from fastapi.testclient import TestClient

class TestUIRefinements(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        self.db_path = self.data_dir / "test_refinements.db"
        self.patcher_db = patch("app.database.DB_PATH", self.db_path)
        self.patcher_api_db = patch("app.routers.api.DB_PATH", self.db_path)
        self.patcher_db.start()
        self.patcher_api_db.start()

        from app.database import init_db, get_db_connection
        init_db()
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO releases (id, url, title, artist, iso_week, is_listened, is_starred, stream_url, tracks_json, bpm, first_synced_at, updated_at)
                   VALUES 
                   (1, 'https://test.bandcamp.com/album/1', 'Test Release 1', 'Artist A', '2026-W39', 0, 0, 'https://test.stream/1', '[]', NULL, '2026-09-21', '2026-09-21'),
                   (2, 'https://test.bandcamp.com/album/2', 'Test Release 2', 'Artist B', '2026-W39', 0, 0, 'https://test.stream/2', '[]', NULL, '2026-09-22', '2026-09-22');"""
            )
            conn.commit()

        from app.main import app
        self.client = TestClient(app)

    @classmethod
    def setUpClass(cls):
        html_path = Path("app/templates/index.html")
        cls.html_content = html_path.read_text(encoding="utf-8")

    def tearDown(self):
        self.patcher_api_db.stop()
        self.patcher_db.stop()
        import gc
        gc.collect()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_bpm_panel_has_standardized_w80_width(self):
        """[Regression Guardrail]: Verify BPM panel container has fixed w-80 (320px) class."""
        self.assertIn('id="bpm-panel"', self.html_content)
        bpm_match = re.search(r'<div[^>]*id="bpm-panel"[^>]*>', self.html_content)
        self.assertIsNotNone(bpm_match)
        bpm_tag = bpm_match.group(0)
        self.assertIn('w-80', bpm_tag)
        self.assertNotIn('w-76', bpm_tag)

    def test_transport_seek_buttons_enlarged_two_steps(self):
        """[Regression Guardrail]: Verify rewind 10s and fast-forward 10s buttons are scaled up to h-9 px-3 text-sm."""
        # Check seekRelative(-10) button
        self.assertIn('onclick="seekRelative(-10)"', self.html_content)
        self.assertIn('onclick="seekRelative(10)"', self.html_content)
        self.assertIn('h-9', self.html_content)
        self.assertIn('px-3', self.html_content)
        self.assertIn('text-sm font-bold', self.html_content)

    def test_weekly_triage_icon_button(self):
        """Verify weekly header renders icon button with unlistened/listened circle check and circular geometry."""
        # Must contain markWeekAllListened with icon display
        self.assertIn("markWeekAllListened", self.html_content)
        self.assertIn("ICON_CHECKED", self.html_content)
        self.assertIn("ICON_UNCHECKED", self.html_content)
        self.assertIn('title="將本週全部標記為已聽"', self.html_content)
        # Concentric circular geometry
        self.assertIn("rounded-full", self.html_content)
        # Plain text '✓ 一鍵已聽' button should be replaced
        self.assertNotIn('>✓ 一鍵已聽<', self.html_content)

    def test_domain_terminology_harmonization(self):
        """Ticket 02 & Ticket 03: Verify Track (曲目) domain term is used and Release base BPM tooltip is present."""
        # Analysis button copy must specifically designate currently playing track
        self.assertIn("分析目前播放曲目 BPM", self.html_content)
        # Contextual tooltip must explain base BPM for Release
        self.assertIn("此 BPM 將作為此 Release 之基準節奏", self.html_content)
        # No Chinese '歌曲' should appear in UI strings
        self.assertNotIn("首歌曲", self.html_content)
        self.assertNotIn("這首歌曲", self.html_content)
        self.assertNotIn("分析目前歌曲", self.html_content)
        # '曲目' must be present
        self.assertIn("曲目", self.html_content)
        # HUD notice must say LISTENED, not COMPLETED
        self.assertIn(": LISTENED", self.html_content)
        self.assertNotIn(": COMPLETED", self.html_content)
        # Sidebar ISO WEEKS standard
        self.assertIn("ISO WEEKS", self.html_content)
        self.assertNotIn("RELEASE WEEKS", self.html_content)
        # Strict negative assertions against barred glossary synonyms (CONTEXT.md)
        self.assertNotIn("ITEM:", self.html_content)
        self.assertNotIn("專輯", self.html_content)
        self.assertNotIn("drawer-album-title", self.html_content)
        self.assertIn("RELEASE:", self.html_content)
        self.assertIn("drawer-release-title", self.html_content)

    def test_bpm_normalization_and_state_machine_templates(self):
        """Verify 70-200 normalization loop, 300 BPM cap, conditional save toggle, and validator."""
        # 70-200 BPM normalization loop
        self.assertIn("while (bpm < 70) bpm *= 2;", self.html_content)
        self.assertIn("while (bpm > 200) bpm /= 2;", self.html_content)
        # Analysis post-check ceiling at 300 BPM
        self.assertIn("estimatedBpm <= 300", self.html_content)
        # Dynamic conditional save button toggle
        self.assertIn("saveBtn.classList.toggle('hidden', !isStagedUnsaved);", self.html_content)
        # Shared client-side validation helper
        self.assertIn("function validateBpm(rawVal)", self.html_content)

    def test_dual_band_web_audio_engine_and_harmonic_comb_filtering(self):
        """Ticket 01 & 03: Verify dual-band filters, 200 Hz frame rate, harmonic comb penalties, and RMS peak segment search."""
        # 1. RMS peak window search
        self.assertIn("findRmsPeakOffset", self.html_content)
        # 2. Dual-band filter separation: Low (180 Hz) and Mid/High (200~2500 Hz) with Q=1.0
        self.assertIn("lowFilter.frequency.value = 180", self.html_content)
        self.assertIn("midFilter.frequency.value = 1000", self.html_content)
        self.assertIn("midFilter.Q.value = 1.0", self.html_content)
        self.assertNotIn("midFilter.Q.value = 0.7", self.html_content)
        # 3. 200 Hz frame rate (5ms hop)
        self.assertIn("sampleRate / 200", self.html_content)
        # 4. Extended autocorrelation lag boundaries (30 to 342)
        self.assertIn("corrMinLag = 30", self.html_content)
        self.assertIn("corrMaxLag = 342", self.html_content)
        # 5. Harmonic comb filtering with 3:4 and 4:3 cross-beat penalties
        self.assertIn("combScore", self.html_content)
        self.assertIn("subLag34", self.html_content)
        self.assertIn("subLag43", self.html_content)
        # 6. Self-documenting variable names (no mysterious abbreviations)
        self.assertIn("sampleLow", self.html_content)
        self.assertIn("sampleMid", self.html_content)
        self.assertIn("diffLow", self.html_content)
        self.assertIn("diffMid", self.html_content)
        self.assertIsNone(re.search(r'\b(diffL|diffM|sL|sM)\b', self.html_content))

    def test_bpm_edit_mode_and_tap_tempo_integration(self):
        """Ticket 02: Verify Tap tempo button, T key binding, 2-sec idle reset, and exclusion of half/double speed buttons."""
        # Tap tempo button and tap count badge in #bpm-edit-mode
        self.assertIn('id="btn-tap-tempo"', self.html_content)
        self.assertIn('handleTapTempo', self.html_content)
        self.assertIn('tapResetTimer', self.html_content)
        # Verify 2000ms idle reset
        self.assertIn('2000', self.html_content)
        # Verify T/t key event listener
        self.assertIn("e.key === 't' || e.key === 'T'", self.html_content)
        # Verify explicit exclusion of half/double speed buttons
        self.assertNotIn('>÷2<', self.html_content)
        self.assertNotIn('>×2<', self.html_content)
        self.assertNotIn('>x2<', self.html_content)
        # Ticket 02 remediation: no auto-focus trapping T key, clampBpm helper, and real-time staged BPM sync
        self.assertNotIn('customInput.focus()', self.html_content)
        self.assertIn('function clampBpm(val)', self.html_content)
        self.assertIn("document.getElementById('staged-bpm-val').innerText = stagedBpm", self.html_content)
        # Focus retention on Tap button and defensive input keydown interception
        self.assertIn("document.getElementById('btn-tap-tempo').focus()", self.html_content)
        self.assertIn("setupCustomBpmInputDefense", self.html_content)

    def test_bulk_listened_api_contract(self):
        """[Regression Guardrail]: Verify POST /api/releases/bulk-listened marks all releases in the specified week as listened."""
        resp = self.client.post("/api/releases/bulk-listened", json={"iso_week": "2026-W39"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")

        from app.database import get_db_connection
        with get_db_connection() as conn:
            rows = conn.execute("SELECT is_listened FROM releases WHERE iso_week = '2026-W39';").fetchall()
            self.assertEqual(len(rows), 2)
            for r in rows:
                self.assertEqual(r["is_listened"], 1)

    def test_sync_limit_selector_present_and_configured(self):
        """Verify sync limit select dropdown, options, persistence key, and startSync limit parameter."""
        self.assertIn('id="sync-limit-select"', self.html_content)
        self.assertIn('value="20"', self.html_content)
        self.assertIn('value="50"', self.html_content)
        self.assertIn('value="100"', self.html_content)
        self.assertIn('value="200"', self.html_content)
        self.assertIn('bandcamp_hub_sync_limit', self.html_content)
        self.assertIn('limit=', self.html_content)

    def test_player_dock_full_width_docked_at_bottom(self):
        """Verify player dock is docked at bottom-0, full-width, with expanded track and center containers."""
        self.assertIn('id="player-dock"', self.html_content)
        # Check player-dock tag classes
        dock_match = re.search(r'<footer[^>]*id="player-dock"[^>]*>', self.html_content)
        self.assertIsNotNone(dock_match)
        dock_tag = dock_match.group(0)
        self.assertIn('bottom-0', dock_tag)
        self.assertIn('w-full', dock_tag)
        self.assertNotIn('bottom-6', dock_tag)

        # Check track title container has max-w-xs
        self.assertIn('max-w-xs', self.html_content)
        # Check center controls has max-w-4xl
        self.assertIn('max-w-4xl', self.html_content)
        # Check drawer has max-w-5xl
        self.assertIn('max-w-5xl', self.html_content)
        # Check bpm-panel has bottom-full mb-3
        self.assertIn('bottom-full mb-3', self.html_content)

    def test_sync_toast_banner_structure_and_behavior(self):
        """Verify #sync-toast-banner, openSettings link, close button, and showSyncToast handler."""
        self.assertIn('id="sync-toast-banner"', self.html_content)
        self.assertIn('showSyncToast', self.html_content)
        self.assertIn('closeSyncToast', self.html_content)
        self.assertIn('closeToast', self.html_content)
        self.assertIn('openSettings();', self.html_content)

    def test_progressive_escape_hierarchy_and_popover_cleanup(self):
        """Verify closePlayer cleans up both bpm-panel and multi-track-drawer, and Escape handling has tiered hierarchy."""
        close_player_match = re.search(r'function closePlayer\(\)\s*\{([^}]+)\}', self.html_content)
        self.assertIsNotNone(close_player_match)
        close_player_body = close_player_match.group(1)
        self.assertIn('multi-track-drawer', close_player_body)
        self.assertIn('bpm-panel', close_player_body)

        # Tiered Escape hierarchy with preventDefault()
        self.assertIn("e.key === 'Escape'", self.html_content)
        self.assertIn('e.preventDefault()', self.html_content)

    def test_absolute_bpm_pitch_stepper_and_fallback(self):
        """Ticket 03: Verify absolute BPM pitch stepper [-1 BPM]/[+1 BPM], 120 fallback, and absence of %."""
        # Stepper buttons must use BPM units
        self.assertIn('>-1 BPM<', self.html_content)
        self.assertIn('>+1 BPM<', self.html_content)
        self.assertIn('原速 (1.0x)', self.html_content)
        self.assertIn('nudgeBpmPitch', self.html_content)
        # Pitch stepper must not contain % labels
        self.assertNotIn('>-1%<', self.html_content)
        self.assertNotIn('>+1%<', self.html_content)
        self.assertNotIn('-20%', self.html_content)
        self.assertNotIn('+20%', self.html_content)
        # 120 fallback baseline for unset base BPM
        self.assertIn('120', self.html_content)
        self.assertIn('(以 120 為基準)', self.html_content)

    def test_deferred_listened_commit_and_anchor_stabilization(self):
        """Ticket 04: Verify deferred listened commit state, commit on release transition, and closePlayer/unload hooks."""
        # 1. Pending listened state variable and helper
        self.assertIn('pendingListenedReleaseId', self.html_content)
        self.assertIn('commitPendingListened', self.html_content)
        # 2. 30s timer sets pending state without calling toggleListen
        self.assertIn('pendingListenedReleaseId = rel.id', self.html_content)
        # 3. Release transition commits previous pending release
        self.assertIn('commitPendingListened(activeRelease.id)', self.html_content)
        # 4. Exit hooks (closePlayer and beforeunload) flush pending commit
        self.assertIn('beforeunload', self.html_content)

if __name__ == "__main__":
    unittest.main()

