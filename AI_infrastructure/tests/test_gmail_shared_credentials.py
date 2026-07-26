"""Regression tests for Gmail's shared Google OAuth credential path."""

import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from google_workspace import gmail


class GmailCredentialPathTests(unittest.TestCase):
    def test_injected_user_uses_shared_gmail_service(self):
        expected_service = object()

        with mock.patch(
            "AI_infrastructure.auth.credential_injector.get_user_gmail_service",
            return_value=expected_service,
        ) as get_service:
            service = gmail._get_gmail_service(
                _user_id=42,
                _injected_credentials=True,
            )

        self.assertIs(service, expected_service)
        get_service.assert_called_once_with(user_id=42)

    def test_missing_injected_credentials_does_not_fall_back(self):
        with self.assertRaisesRegex(Exception, "MUST call Gmail tools through"):
            gmail._get_gmail_service(_user_id=42, _injected_credentials=False)

    def test_gmail_module_has_no_direct_credentials_constructor(self):
        source = Path(gmail.__file__).read_text(encoding="utf-8")

        self.assertNotIn("credentials = Credentials(", source)
        self.assertNotIn("build('gmail', 'v1', credentials=credentials)", source)


if __name__ == "__main__":
    unittest.main()
