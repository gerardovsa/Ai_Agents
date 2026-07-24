"""Regression tests for the Anthropic web_search country code sanitizer.

Background
----------
Anthropic's ``web_search_20250305`` server tool rejects
``user_location.country`` values longer than 2 characters with HTTP 400
(``String should have at most 2 characters``). The
``ai_infrastructure.user_preferences`` table historically stored the full
country NAME (e.g. ``"Australia"``) under ``detected_country`` and a route
forwarded that string into the ``"country"`` key of the location dict.
:func:`AI_infrastructure.core.ip_location.build_context_from_stored_location`
now sanitises that key with :func:`_safe_iso_country` so the default 2-letter
code (e.g. ``"AU"``) survives the merge when the stored value is not a
valid ISO 3166-1 alpha-2 code.

These tests pin the new contract.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from AI_infrastructure.core import ip_location  # noqa: E402
from AI_infrastructure.core.ip_location import (  # noqa: E402
    _safe_iso_country,
    build_context_from_stored_location,
)


class SafeIsoCountryHelperTests(unittest.TestCase):
    """Direct unit tests for the ``_safe_iso_country`` helper."""

    def test_returns_none_for_full_country_name(self):
        self.assertIsNone(_safe_iso_country('Australia'))

    def test_returns_none_for_lowercase_full_name(self):
        self.assertIsNone(_safe_iso_country('australia'))

    def test_returns_none_for_three_letter_code(self):
        self.assertIsNone(_safe_iso_country('USA'))

    def test_returns_none_for_none(self):
        self.assertIsNone(_safe_iso_country(None))

    def test_returns_none_for_empty_string(self):
        self.assertIsNone(_safe_iso_country(''))

    def test_returns_none_for_whitespace_only(self):
        self.assertIsNone(_safe_iso_country('   '))

    def test_returns_none_for_non_string(self):
        self.assertIsNone(_safe_iso_country(42))
        self.assertIsNone(_safe_iso_country(['AU']))
        self.assertIsNone(_safe_iso_country({'code': 'AU'}))

    def test_returns_value_for_two_letter_code(self):
        self.assertEqual(_safe_iso_country('AU'), 'AU')

    def test_returns_value_for_non_au_two_letter_code(self):
        self.assertEqual(_safe_iso_country('US'), 'US')

    def test_normalises_lowercase_two_letter_to_upper(self):
        self.assertEqual(_safe_iso_country('au'), 'AU')

    def test_normalises_whitespace_around_two_letter_code(self):
        self.assertEqual(_safe_iso_country('  NZ  '), 'NZ')

    def test_rejects_two_chars_that_are_not_alpha(self):
        self.assertIsNone(_safe_iso_country('A1'))
        self.assertIsNone(_safe_iso_country('1A'))


class BuildContextCountrySanitisationTests(unittest.TestCase):
    """``build_context_from_stored_location`` must never forward a
    non-ISO-3166-1 country code to downstream consumers (Anthropic
    web_search, etc.). The temporal/weather side is mocked to keep these
    tests fast and offline.
    """

    def _ctx(self, stored):
        with mock.patch.object(
            ip_location, '_add_temporal_data', side_effect=lambda d: d
        ):
            return build_context_from_stored_location(stored)

    def test_drops_full_country_name_and_falls_back_to_default(self):
        ctx = self._ctx({'country': 'Australia'})
        self.assertEqual(ctx['country'], 'AU')

    def test_keeps_valid_two_letter_code(self):
        ctx = self._ctx({'country': 'AU'})
        self.assertEqual(ctx['country'], 'AU')

    def test_keeps_non_au_two_letter_code(self):
        ctx = self._ctx({'country': 'US'})
        self.assertEqual(ctx['country'], 'US')

    def test_drops_none_value(self):
        ctx = self._ctx({'country': None})
        self.assertEqual(ctx['country'], 'AU')

    def test_drops_empty_string(self):
        ctx = self._ctx({'country': ''})
        self.assertEqual(ctx['country'], 'AU')

    def test_drops_three_letter_code(self):
        ctx = self._ctx({'country': 'USA'})
        self.assertEqual(ctx['country'], 'AU')

    def test_drops_lowercase_full_name(self):
        ctx = self._ctx({'country': 'australia'})
        self.assertEqual(ctx['country'], 'AU')

    def test_normalises_lowercase_two_letter_to_upper(self):
        ctx = self._ctx({'country': 'au'})
        self.assertEqual(ctx['country'], 'AU')

    def test_country_name_is_preserved_alongside_sanitised_country(self):
        # Mirrors the original route shape: country name is forwarded under
        # 'country_name' (correct) and was previously ALSO forwarded under
        # 'country' (the bug). The full name should still surface for display.
        ctx = self._ctx({
            'country': 'Australia',
            'country_name': 'Australia',
        })
        self.assertEqual(ctx['country'], 'AU')
        self.assertEqual(ctx['country_name'], 'Australia')

    def test_only_country_key_is_sanitised(self):
        # Other stored fields should pass through unchanged.
        ctx = self._ctx({
            'country': 'Australia',
            'city': 'Brisbane',
            'region': 'Queensland',
            'timezone': 'Australia/Brisbane',
        })
        self.assertEqual(ctx['country'], 'AU')
        self.assertEqual(ctx['city'], 'Brisbane')
        self.assertEqual(ctx['region'], 'Queensland')
        self.assertEqual(ctx['timezone'], 'Australia/Brisbane')

    def test_realistic_route_payload_no_longer_triggers_400(self):
        # Replay the shape that the production route was sending before
        # the fix. The full name is the only value the schema exposes for
        # the country; downstream must not see a >2 char string.
        ctx = self._ctx({
            'city': 'Brisbane',
            'country': 'Australia',          # full name (would 400 Anthropic)
            'country_name': 'Australia',     # correct slot for the full name
            'timezone': 'Australia/Brisbane',
        })
        # Anthropic's hard limit
        self.assertLessEqual(len(ctx['country']), 2)
        # And specifically the default we want for this user
        self.assertEqual(ctx['country'], 'AU')


class BuildContextEndToEndTests(unittest.TestCase):
    """Smoke test: the full function still runs without mocking
    ``_add_temporal_data``. We avoid the network by not passing
    latitude/longitude (so weather is skipped) and we only assert on the
    sanitised country field.
    """

    def test_full_function_runs_and_sanitises_country(self):
        ctx = build_context_from_stored_location({
            'country': 'Australia',
            'country_name': 'Australia',
        })
        self.assertEqual(ctx['country'], 'AU')
        self.assertEqual(ctx['country_name'], 'Australia')


if __name__ == '__main__':
    unittest.main()
