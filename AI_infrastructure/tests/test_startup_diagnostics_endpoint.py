"""Test: Startup Diagnostics Endpoints

Verifies the two diagnostic views added to dev_tools_bp:

- GET /api/dev-tools/startup-diagnostics       (JSON)
- GET /api/dev-tools/startup-diagnostics.txt   (plain text)

These views are protected by the production `@require_auth` decorator
chain (auth.user_auth.require_auth) plus an in-handler role check
(_require_admin_or_owner → PermissionChecker.has_role_level).

Testing strategy
----------------
We cannot easily exercise the real `@require_auth` decorator without
booting the full Flask app (JWT, DB, sockets, etc.). Instead we
construct a fresh Flask app in the test that:

1. Registers a `before_request` hook that sets `request.user` from a
   request header (`X-Test-User-Id`, `X-Test-Is-Admin`).
2. Re-registers the SAME two route URL rules on a fresh blueprint,
   but with view functions that share their bodies with the production
   views (i.e. they call the same `_require_admin_or_owner` helper and
   the same `snapshot()`/`render_text()` functions).

This validates the gating logic and response shape without booting the
production app. Integration verification against a running Render
service is left to the curl smoke checks in the plan's Verification
section.

Tests:
1. unauthenticated → 401
2. authenticated non-admin → 403
3. authenticated admin → 200 with the documented JSON shape
4. authenticated admin → 200 plain-text body with the table header

Run:
    cd AI_infrastructure
    python tests/test_startup_diagnostics_endpoint.py
"""
import json
import os
import sys
import unittest
from unittest.mock import patch

from flask import Blueprint, Flask, Response, jsonify, request

# Allow running from the AI_infrastructure directory.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from AI_infrastructure.shared import startup_timing as st  # noqa: E402
# Import the helper directly. We do NOT call its view functions because
# they are wrapped by the real @require_auth decorator — instead we
# register new routes below that call the same body code.
from AI_infrastructure.routes.dev_tools_routes import _require_admin_or_owner  # noqa: E402


# ============================================================================
# Test blueprint — mirrors the two new views without the @require_auth wrapper
# ============================================================================
test_bp = Blueprint("test_startup_diag", __name__, url_prefix="/api/dev-tools")


@test_bp.route("/startup-diagnostics", methods=["GET"])
def _json_view():
    """Mirror of dev_tools_routes.startup_diagnostics_json, minus @require_auth."""
    ok, err_resp, _uid = _require_admin_or_owner()
    if not ok:
        return err_resp
    return jsonify(st.snapshot())


@test_bp.route("/startup-diagnostics.txt", methods=["GET"])
def _text_view():
    """Mirror of dev_tools_routes.startup_diagnostics_text, minus @require_auth."""
    ok, err_resp, _uid = _require_admin_or_owner()
    if not ok:
        return err_resp
    return Response(st.render_text(), mimetype="text/plain")


def _build_test_app():
    """Build a Flask app that uses a `before_request` hook to populate
    `request.user` from headers, then mounts the test blueprint above.
    """
    app = Flask(__name__)

    @app.before_request
    def _stub_user():
        user_id = request.headers.get("X-Test-User-Id")
        if user_id is not None:
            # Stash on the request object exactly like @require_auth does.
            request.user = {"user_id": int(user_id)}

    app.register_blueprint(test_bp)
    return app


class _FakePermissionChecker:
    """Drop-in for PermissionChecker() that returns a configurable level."""

    def __init__(self, level):
        self._level = level

    def has_role_level(self, user_id, required):
        return self._level >= required


class TestStartupDiagnosticsEndpoint(unittest.TestCase):

    def setUp(self):
        st._reset_for_tests()
        # Seed two fake phases so the response is non-empty.
        st.begin("phase_a")
        st.end("phase_a", note="seeded A")
        st.begin("phase_b")
        st.end("phase_b", note="seeded B")
        self.app = _build_test_app()
        self.client = self.app.test_client()

    def tearDown(self):
        st._reset_for_tests()

    # ------------------------------------------------------------------ JSON
    def test_json_unauthenticated_returns_401(self):
        resp = self.client.get("/api/dev-tools/startup-diagnostics")
        self.assertEqual(resp.status_code, 401)
        body = resp.get_json()
        self.assertEqual(body.get("ok"), False)
        self.assertEqual(body.get("error"), "unauthenticated")

    def test_json_non_admin_returns_403(self):
        with patch("auth.permission_checker.PermissionChecker") as PC:
            PC.return_value = _FakePermissionChecker(level=2)
            resp = self.client.get(
                "/api/dev-tools/startup-diagnostics",
                headers={"X-Test-User-Id": "42"},
            )
        self.assertEqual(resp.status_code, 403)
        body = resp.get_json()
        self.assertEqual(body.get("error"), "forbidden")

    def test_json_admin_returns_200_with_phases(self):
        with patch("auth.permission_checker.PermissionChecker") as PC:
            PC.return_value = _FakePermissionChecker(level=5)
            resp = self.client.get(
                "/api/dev-tools/startup-diagnostics",
                headers={"X-Test-User-Id": "1"},
            )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertTrue(body.get("ok"))
        self.assertIn("phases", body)
        self.assertIn("summary", body)
        self.assertIn("boot_total_ms", body)
        self.assertEqual(len(body["phases"]), 2)
        ids = [p["id"] for p in body["phases"]]
        self.assertIn("phase_a", ids)
        self.assertIn("phase_b", ids)

    # ------------------------------------------------------------------ text
    def test_text_admin_returns_table(self):
        with patch("auth.permission_checker.PermissionChecker") as PC:
            PC.return_value = _FakePermissionChecker(level=5)
            resp = self.client.get(
                "/api/dev-tools/startup-diagnostics.txt",
                headers={"X-Test-User-Id": "1"},
            )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/plain", resp.headers.get("Content-Type", ""))
        body = resp.get_data(as_text=True)
        self.assertIn("phase_a", body)
        self.assertIn("phase_b", body)
        self.assertIn("TOTAL BOOT", body)
        self.assertIn("UNDER_5S_TARGET", body)

    def test_text_unauthenticated_returns_401(self):
        resp = self.client.get("/api/dev-tools/startup-diagnostics.txt")
        self.assertEqual(resp.status_code, 401)


def main():
    print("=" * 70)
    print("STARTUP DIAGNOSTICS ENDPOINT — TESTS")
    print("=" * 70)
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
