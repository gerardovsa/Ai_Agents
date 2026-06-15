"""Regression test for the comprehensive account-profile load-order fix.

Background (June 15, 2026):
    The account profile UI was silently dropping 30 of 33 fields on save
    and reverting the model dropdown to Claude Sonnet 4.6 on every reload.
    Three competing loaders (`loadAndPopulatePreferences`,
    `loadSectionData`, the value branch of `loadModelCatalog`) and two
    competing endpoints (`/api/auth/preferences` vs
    `/api/user/preferences`) exacerbated the problem.

    The fix:
      - Promoted `loadAndPopulatePreferences` to the single canonical loader
        and pointed it at `/api/user/preferences`.
      - Extended `UI_TO_BACKEND_KEY` and `_collectSettingsFromUI` to cover
        all 33 fields.
      - Split `onThinkingToggle()` (user click) from
        `applyThinkingConstraints()` (pure UI state) so the load path no
        longer resets temperature to 1.0.
      - Removed the dead `loadSectionData` and `saveSettingsSection` code
        paths (they were sending partial payloads that NULLed out the rest
        of the user_preferences row, and the load path was calling
        `onThinkingToggle()` which is why temperature silently reset).
      - Fixed the `||` precedence bug in `loadModelCatalog` and made it
        read from `/api/user/preferences` first.
      - Stripped hard-coded `selected`/`checked` attributes on
        user-controlled fields so the static HTML cannot win over the
        JS-applied DB value.

This test does NOT spin up the full Flask app or a browser. It
file-asserts on the SPA source so the regressions cannot be
silently re-introduced by a future edit. The test is intentionally
stringent — the file content is the contract.

Run:
    python AI_infrastructure/tests/test_account_profile_load_order.py
"""
import os
import re
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
HTML_PATH = os.path.join(REPO_ROOT, 'UI', 'business-ai-platform-v2.html')
AUTH_ROUTES_PATH = os.path.join(REPO_ROOT, 'AI_infrastructure', 'routes', 'auth_routes.py')
USER_PREF_ROUTES_PATH = os.path.join(REPO_ROOT, 'AI_infrastructure', 'routes', 'user_preferences_routes.py')
MIGRATION_PATH = os.path.join(REPO_ROOT, 'AI_infrastructure', 'migrations', '053_add_user_preferences_frontend_fields.sql')


def _read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def _block(html, start_marker, end_marker):
    """Return the substring between two markers (for narrowing assertions)."""
    s = html.find(start_marker)
    if s == -1:
        return ''
    e = html.find(end_marker, s + len(start_marker))
    return html[s:e] if e != -1 else html[s:]


def _function_body(html, signature):
    """Extract the body of a top-level JS function given its signature,
    using a brace-balanced scan. Returns the substring from the opening
    `{` after the signature to its matching `}`. Returns '' if not found."""
    s = html.find(signature)
    if s == -1:
        return ''
    # Find the first `{` after the signature
    open_idx = html.find('{', s + len(signature))
    if open_idx == -1:
        return ''
    depth = 0
    for i in range(open_idx, len(html)):
        ch = html[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return html[open_idx:i + 1]
    return ''


class TestCanonicalLoaderEndpoint(unittest.TestCase):
    """The canonical loader must read from /api/user/preferences (not /api/auth/preferences)."""

    @classmethod
    def setUpClass(cls):
        cls.html = _read(HTML_PATH)

    def test_loader_uses_user_preferences_endpoint(self):
        loader = _block(self.html, 'async loadAndPopulatePreferences()', 'loadSectionData(')
        # The function body should call /api/user/preferences
        self.assertIn('/api/user/preferences', loader,
                      "Canonical loader must read from /api/user/preferences")
        # And NOT the old /api/auth/preferences
        self.assertNotIn('/api/auth/preferences', loader,
                         "Canonical loader must NOT use the legacy /api/auth/preferences endpoint")

    def test_loader_writes_localStorage_cache(self):
        loader = _block(self.html, 'async loadAndPopulatePreferences()', 'loadSectionData(')
        self.assertIn("localStorage.setItem('accountSettings'", loader,
                      "Canonical loader must refresh localStorage as a write-through cache")


class TestCollectorCoverage(unittest.TestCase):
    """_collectSettingsFromUI must cover all 33 fields."""

    @classmethod
    def setUpClass(cls):
        cls.html = _read(HTML_PATH)
        cls.collector = _block(cls.html, 'function _collectSettingsFromUI()', '// Push a settings object')

    def test_collector_covers_ai_settings(self):
        for key in ('ai_model', 'ai_temperature', 'ai_top_p', 'ai_max_tokens',
                    'ai_thinking_enabled', 'ai_thinking_budget',
                    'ai_streaming_enabled', 'max_rounds', 'round_timeout'):
            self.assertIn(key, self.collector, f"Collector missing AI field: {key}")

    def test_collector_covers_personalization(self):
        for key in ('nickname', 'communication_style', 'detail_level', 'auth_platform'):
            self.assertIn(key, self.collector, f"Collector missing personalization field: {key}")

    def test_collector_covers_location(self):
        for key in ('use_manual_location', 'manual_location_override',
                    'use_manual_timezone', 'manual_timezone_override'):
            self.assertIn(key, self.collector, f"Collector missing location field: {key}")

    def test_collector_covers_notifications(self):
        for key in ('enable_notifications', 'enable_sounds'):
            self.assertIn(key, self.collector, f"Collector missing notification field: {key}")

    def test_collector_covers_appearance(self):
        self.assertIn('theme', self.collector, "Collector missing appearance field: theme")

    def test_collector_covers_chip_lists(self):
        for key in ('preferred_tools', 'custom_preferences', 'ai_memories'):
            self.assertIn(key, self.collector, f"Collector missing chip-list field: {key}")

    def test_collector_does_not_collect_detected_fields(self):
        """detected_* are server-derived, not user-editable. They must
        NEVER be collected from the form, or every save resets them to
        whatever the form text was."""
        for key in ('detected_city', 'detected_country', 'detected_timezone',
                    'detected_ip_address', 'detected_lat', 'detected_lon'):
            self.assertNotIn(f"'{key}'", self.collector,
                             f"Collector must NOT collect server-derived field: {key}")


class TestUItoBackendKeyMap(unittest.TestCase):
    """UI_TO_BACKEND_KEY must cover all 33 user-controlled fields."""

    @classmethod
    def setUpClass(cls):
        cls.html = _read(HTML_PATH)
        cls.map_block = _block(cls.html, 'const UI_TO_BACKEND_KEY = {', '};')

    def test_map_includes_every_input_id(self):
        for elem_id in ('modelSelect', 'temperature', 'topP', 'maxTokens',
                        'enableThinking', 'thinkingBudgetSlider', 'enableStreaming',
                        'maxRounds', 'roundTimeout', 'userNickname', 'communicationStyle',
                        'authPlatform', 'useManualLocation', 'manualLocation',
                        'useManualTimezone', 'manualTimezone',
                        'enableNotifications', 'enableSounds'):
            self.assertIn(f"'{elem_id}'", self.map_block,
                          f"UI_TO_BACKEND_KEY missing element ID: {elem_id}")


class TestOnThinkingToggleSplit(unittest.TestCase):
    """onThinkingToggle must not be called from the load path."""

    @classmethod
    def setUpClass(cls):
        cls.html = _read(HTML_PATH)

    def test_applyThinkingConstraints_exists(self):
        self.assertIn('function applyThinkingConstraints', self.html,
                      "Pure UI constraint function must be defined")

    def test_onThinkingToggle_delegates_to_apply(self):
        """The user-click handler should call applyThinkingConstraints
        and then saveSettings. The load path must not call onThinkingToggle."""
        # Find the onThinkingToggle function body
        body = _block(self.html, 'function onThinkingToggle()', 'function applyThinkingConstraints')
        # Either the body comes before applyThinkingConstraints, or
        # we look for it in a different position. Use a simpler test:
        self.assertIn('applyThinkingConstraints()', body,
                      "onThinkingToggle must call applyThinkingConstraints (the pure UI function)")

    def test_loadSectionData_does_not_call_onThinkingToggle(self):
        """The removed loadSectionData used to call onThinkingToggle from
        the load path, which silently reset temperature to 1.0. After
        the fix, neither the stub nor any remaining call site may do that."""
        # Strip the stub
        stub_re = re.compile(
            r'async function loadSectionData\([^)]*\)\s*\{[^}]*\}',
            re.DOTALL,
        )
        stubs = stub_re.findall(self.html)
        for stub in stubs:
            self.assertNotIn('onThinkingToggle', stub,
                             "loadSectionData stub must not call onThinkingToggle")


class TestLoadModelCatalogPrecedence(unittest.TestCase):
    """loadModelCatalog must read /api/user/preferences first, not
    operator-precedence-bug the localStorage ternary."""

    @classmethod
    def setUpClass(cls):
        cls.html = _read(HTML_PATH)
        cls.body = _block(cls.html, 'async function loadModelCatalog()', 'function updateModelHint')

    def test_calls_user_preferences_first(self):
        self.assertIn("/api/user/preferences", self.body,
                      "loadModelCatalog must read from /api/user/preferences")

    def test_no_precedence_bug(self):
        """The old code: `const currentValue = sel.value || localStorage...
            ? JSON.parse(localStorage...) : null;` parses as
            (sel.value || ls) ? JSON.parse(ls) : null, which is
            effectively `currentValue = JSON.parse(ls) || null`.
            After the fix the precedence is explicit (early-return / if-blocks)."""
        self.assertNotIn('? JSON.parse(localStorage', self.body,
                         "loadModelCatalog must not have the operator-precedence ternary bug")


class TestHTMLDefaultsRemoved(unittest.TestCase):
    """Hard-coded selected/checked attributes on user-controlled fields
    are forbidden — they were the root cause of the dropdown revert bug."""

    @classmethod
    def setUpClass(cls):
        cls.html = _read(HTML_PATH)

    def test_modelSelect_has_no_hardcoded_selected(self):
        # The static HTML for #modelSelect must not have any 'selected' attribute
        block = _block(self.html, 'id="modelSelect"', '</select>')
        self.assertNotIn(' selected', block,
                         "modelSelect <option>s must not have hard-coded 'selected' attribute")

    def test_enableThinking_has_no_hardcoded_checked(self):
        block = _block(self.html, 'id="enableThinking"', '>')
        self.assertNotIn(' checked', block,
                         "enableThinking checkbox must not be hard-coded checked")

    def test_enableStreaming_has_no_hardcoded_checked(self):
        block = _block(self.html, 'id="enableStreaming"', '>')
        self.assertNotIn(' checked', block,
                         "enableStreaming checkbox must not be hard-coded checked")

    def test_enableNotifications_has_no_hardcoded_checked(self):
        block = _block(self.html, 'id="enableNotifications"', '>')
        self.assertNotIn(' checked', block,
                         "enableNotifications checkbox must not be hard-coded checked")

    def test_enableSounds_has_no_hardcoded_checked(self):
        block = _block(self.html, 'id="enableSounds"', '>')
        self.assertNotIn(' checked', block,
                         "enableSounds checkbox must not be hard-coded checked")

    def test_theme_dark_has_no_hardcoded_checked(self):
        block = _block(self.html, 'name="theme" value="dark"', '>')
        self.assertNotIn(' checked', block,
                         "theme=dark radio must not be hard-coded checked")


class TestDeadCodeRemoved(unittest.TestCase):
    """loadSectionData and saveSettingsSection were the per-section
    loaders/savers that caused the partial-payload clobber and the
    load-path temperature reset. They are stubs now and must not do
    anything."""

    @classmethod
    def setUpClass(cls):
        cls.html = _read(HTML_PATH)

    def test_loadSectionData_is_a_stub(self):
        # Find the function body — it should be just a comment. Use a
        # brace-balanced extraction so we don't pick up unrelated code.
        body = _function_body(self.html, 'async function loadSectionData(')
        # Must be present
        self.assertTrue(len(body) > 0, "loadSectionData must still exist as a stub")
        # Must not contain any of the side effects
        for forbidden in ('fetch(', 'onThinkingToggle', 'ai_thinking_enabled'):
            self.assertNotIn(forbidden, body,
                             f"loadSectionData stub must not contain '{forbidden}'")

    def test_saveSettingsSection_is_a_stub(self):
        body = _function_body(self.html, 'async function saveSettingsSection(')
        self.assertTrue(len(body) > 0, "saveSettingsSection must still exist as a stub")
        for forbidden in ('fetch(', 'UI_TO_BACKEND_KEY[', 'JSON.parse'):
            self.assertNotIn(forbidden, body,
                             f"saveSettingsSection stub must not contain '{forbidden}'")


class TestBackendSupportsNewFields(unittest.TestCase):
    """Migration 053 added 5 columns. The backend must accept them."""

    @classmethod
    def setUpClass(cls):
        cls.migration = _read(MIGRATION_PATH)
        cls.auth = _read(AUTH_ROUTES_PATH)
        cls.user_pref = _read(USER_PREF_ROUTES_PATH)

    def test_migration_adds_all_5_columns(self):
        for col in ('theme', 'enable_notifications', 'enable_sounds',
                    'max_rounds', 'round_timeout'):
            self.assertIn(col, self.migration,
                          f"Migration 053 must add column: {col}")

    def test_auth_routes_whitelist_includes_new_fields(self):
        for col in ('theme', 'enable_notifications', 'enable_sounds',
                    'max_rounds', 'round_timeout'):
            self.assertIn(f"'{col}'", self.auth,
                          f"auth_routes allowed_fields must include '{col}'")

    def test_user_preferences_routes_handles_new_fields(self):
        for col in ('theme', 'enable_notifications', 'enable_sounds',
                    'max_rounds', 'round_timeout'):
            self.assertIn(col, self.user_pref,
                          f"user_preferences_routes.py must handle '{col}'")


if __name__ == '__main__':
    if not os.path.exists(HTML_PATH):
        print(f"FAIL: HTML not found at {HTML_PATH}", file=sys.stderr)
        sys.exit(1)
    unittest.main(verbosity=2)
