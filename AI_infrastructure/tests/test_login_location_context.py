"""Regression tests for login-stored location and fresh chat context.

Run:
    python AI_infrastructure/tests/test_login_location_context.py
"""
import os
import sys
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from AI_infrastructure.core import ip_location


class TestStoredLocationContext(unittest.TestCase):
    def setUp(self):
        with ip_location._weather_cache_lock:
            ip_location._weather_cache.clear()

    @patch.object(ip_location, 'get_location_from_ip')
    @patch.object(ip_location, '_fetch_weather_data')
    def test_chat_context_uses_coordinates_without_ip_lookup(self, fetch_weather, resolve_ip):
        fetch_weather.return_value = {
            'temperature_c': 24.0,
            'temperature_f': 75.2,
            'weather_condition': 'Clear sky',
            'weather_code': 0,
        }

        context = ip_location.build_context_from_stored_location({
            'city': 'Brisbane',
            'country_name': 'Australia',
            'timezone': 'Australia/Brisbane',
            'latitude': -27.47,
            'longitude': 153.02,
            'location_string': 'Brisbane, Australia',
        })

        resolve_ip.assert_not_called()
        self.assertEqual(context['temperature_c'], 24.0)
        self.assertIn('current_time', context)
        self.assertIn('month_name', context)

    @patch.object(ip_location, '_fetch_weather_data')
    def test_weather_is_cached_by_coordinates(self, fetch_weather):
        fetch_weather.return_value = {
            'temperature_c': 20.0,
            'temperature_f': 68.0,
            'weather_condition': 'Clear sky',
            'weather_code': 0,
        }
        location = {
            'timezone': 'Australia/Brisbane',
            'latitude': -27.47,
            'longitude': 153.02,
        }

        ip_location.build_context_from_stored_location(location)
        ip_location.build_context_from_stored_location(location)

        fetch_weather.assert_called_once()

    @patch.object(ip_location, '_fetch_weather_data')
    def test_missing_coordinates_omits_weather(self, fetch_weather):
        context = ip_location.build_context_from_stored_location({
            'timezone': 'Australia/Brisbane',
            'city': 'Brisbane',
        })

        fetch_weather.assert_not_called()
        self.assertNotIn('temperature_c', context)
        self.assertNotEqual(context['current_time'], 'Unknown')

    @patch.object(ip_location.requests, 'get')
    def test_failed_ip_lookup_is_not_marked_resolved(self, get_request):
        get_request.side_effect = ip_location.requests.exceptions.Timeout()

        location = ip_location.get_location_from_ip('203.0.113.1')

        self.assertFalse(location['resolved_from_ip'])
        self.assertNotIn('current_time', location)

    def test_manual_overrides_apply_without_ip_lookup(self):
        context = ip_location.build_context_from_stored_location(
            {'timezone': 'Australia/Brisbane'},
            location_override='Perth, Australia',
            timezone_override='Australia/Perth',
        )

        self.assertEqual(context['location_string'], 'Perth, Australia')
        self.assertEqual(context['timezone'], 'Australia/Perth')


class TestActiveCallPaths(unittest.TestCase):
    def test_chat_stream_has_no_ip_location_lookup(self):
        path = os.path.join(REPO_ROOT, 'AI_infrastructure', 'routes', 'agent_routes_v4.py')
        with open(path, 'r', encoding='utf-8') as handle:
            source = handle.read()
        start = source.index('# STORED LOCATION + FRESH TIME/WEATHER')
        end = source.index('# SERVER TOOLS', start)
        block = source[start:end]

        self.assertNotIn('request.remote_addr', block)
        self.assertNotIn('get_location_dict', block)
        self.assertNotIn('get_location_from_ip', block)
        self.assertIn('build_context_from_stored_location', block)

    def test_browser_does_not_call_ipapi(self):
        path = os.path.join(
            REPO_ROOT, 'UI', 'modules_internal', 'components', 'account_profile.js'
        )
        with open(path, 'r', encoding='utf-8') as handle:
            source = handle.read()

        self.assertNotIn('https://ipapi.co', source)
        self.assertIn('geolocationDetectionPromise', source)
        self.assertIn('payload.data || payload', source)


if __name__ == '__main__':
    unittest.main()
