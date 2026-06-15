"""
Debug Agent — Background Probe Loop
=====================================
Polls the platform's own ``/api/admin/diagnostics/summary`` endpoint on a
schedule, cross-references with the Render service state, and emits alerts
to Sentry + Slack + the local log stream.

Why both probes?
  * ``/api/admin/diagnostics/summary`` — the platform's *internal* view
    (in-process probes). Fast, no extra HTTP.
  * Render service state — the *host* view. The container may be running
    but the service suspended at Render, or a deploy may have just failed.
    Combining both catches "the app says it's fine, but Render is paused".

Usage:
  # One-shot probe (for CI / manual)
  python -m monitoring.debug_agent check

  # Continuous daemon (for the server itself, or a sidecar)
  python -m monitoring.debug_agent daemon --interval 300

  # Self-heal: if /health fails 3x in a row, restart via Render API
  python -m monitoring.debug_agent daemon --interval 60 --auto-heal

Env vars consumed:
  DEBUG_AGENT_INTERVAL_SEC    — polling cadence (default 300)
  DEBUG_AGENT_AUTO_HEAL       — set "true" to enable Render restart on
                                 sustained health failure (default false)
  DEBUG_AGENT_HEALTH_FAIL_THRESHOLD — consecutive failures before
                                 auto-heal triggers (default 3)
  DEBUG_AGENT_AUTH_TOKEN      — JWT to send on the diagnostics probe
                                 (required for /api/admin/diagnostics)
  RENDER_API_KEY              — Render REST API token
  RENDER_SERVICE_ID           — the service ID to monitor (also in env
                                 already per .env.example)
  SENTRY_DSN                  — Sentry DSN (already optional)
  SLACK_WEBHOOK_URL           — Slack incoming webhook for alerts
  PLATFORM_BASE_URL           — e.g. https://ai-agents-v10.onrender.com
                                 (default: derived from RENDER_SERVICE_ID
                                 — not always accurate, prefer setting it)

Author: Cleanup round 2 (June 15, 2026)
"""
import argparse
import json
import os
import signal
import sys
import time
import logging
import threading
from datetime import datetime, UTC
from typing import Optional, Dict, Any

# Importing locally-installed monitoring helpers
from monitoring.render_client import RenderClient

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger('debug_agent')
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [DEBUG_AGENT] %(levelname)-7s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%z'
    ))
    logger.addHandler(handler)
    logger.setLevel(os.getenv('DEBUG_AGENT_LOG_LEVEL', 'INFO').upper())


# ---------------------------------------------------------------------------
# Probe + Alert helpers
# ---------------------------------------------------------------------------

def _http_get_json(url: str, token: Optional[str] = None, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """GET <url> with optional Bearer token. Returns parsed JSON or None."""
    try:
        import requests
    except ImportError:
        logger.error('requests not installed — cannot probe')
        return None
    headers = {'Accept': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:  # requests.RequestException or JSON parse
        logger.warning(f'GET {url} failed: {e}')
        return None


def _send_slack(message: str) -> bool:
    """Best-effort Slack webhook post. Returns True if sent (or skipped because not configured)."""
    webhook = os.getenv('SLACK_WEBHOOK_URL', '').strip()
    if not webhook:
        logger.info('[ALERT] (slack skipped — SLACK_WEBHOOK_URL not set) %s', message)
        return True  # not a failure, just no sink
    try:
        import requests
        r = requests.post(webhook, json={'text': message}, timeout=5)
        r.raise_for_status()
        logger.info('[ALERT] sent to slack')
        return True
    except Exception as e:
        logger.error(f'[ALERT] slack post failed: {e}')
        return False


def _send_sentry(level: str, message: str, extra: Optional[dict] = None) -> None:
    """Best-effort Sentry message. Returns silently if SDK isn't init'd."""
    try:
        import sentry_sdk
        sentry_sdk.capture_message(message, level=level, extras=extra or {})
    except ImportError:
        logger.info(f'[ALERT] (sentry skipped — SDK not installed) {message}')
    except Exception as e:
        logger.error(f'[ALERT] sentry post failed: {e}')


def _alert(severity: str, summary: str, details: Dict[str, Any]) -> None:
    """
    Fan out an alert to all configured sinks. ``severity`` is one of
    info / warning / error / fatal — passed through to Sentry and used
    to pick a Slack emoji prefix.
    """
    emoji = {
        'info': 'ℹ️', 'warning': '⚠️', 'error': '🔴', 'fatal': '💀',
    }.get(severity, 'ℹ️')
    slack_msg = f'{emoji} *AI Agents — {severity.upper()}*\n{summary}\n```{json.dumps(details, indent=2, default=str)[:1800]}```'
    _send_sentry(severity, summary, details)
    _send_slack(slack_msg)
    logger.log(
        {'info': logging.INFO, 'warning': logging.WARNING,
         'error': logging.ERROR, 'fatal': logging.CRITICAL}.get(severity, logging.INFO),
        f'[ALERT] {severity}: {summary}'
    )


# ---------------------------------------------------------------------------
# Core probe + decision logic
# ---------------------------------------------------------------------------

def _classify(probe: Dict[str, Any], render_state: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Given the platform probe and the Render service state, decide if an
    alert is warranted. Returns ``None`` if all is well, or a dict
    ``{'severity': 'warning'|'error'|'fatal', 'summary': str, 'details': dict}``.
    """
    status = (probe or {}).get('status', 'unknown')
    details = {
        'probe_status': status,
        'probe_duration_ms': (probe or {}).get('duration_ms'),
        'render_state': (render_state or {}).get('state') if render_state else 'unknown',
        'render_last_deploy': (render_state or {}).get('last_deploy', {}).get('status') if render_state else None,
    }
    # Hardest case: the platform says unhealthy
    if status == 'unhealthy':
        return {
            'severity': 'error',
            'summary': 'Platform diagnostics returned unhealthy',
            'details': details,
        }
    if status == 'degraded':
        return {
            'severity': 'warning',
            'summary': 'Platform diagnostics degraded (some probes failing)',
            'details': details,
        }
    # Platform says healthy but Render service is suspended — silent
    # failure that needs the human to fix
    if render_state and render_state.get('state') == 'suspended':
        return {
            'severity': 'fatal',
            'summary': 'Platform healthy but Render service is suspended',
            'details': details,
        }
    return None


def _do_probe(platform_url: str, token: Optional[str], render: Optional[RenderClient], service_id: Optional[str]) -> Dict[str, Any]:
    """
    Run a single probe cycle. Always returns a dict so the caller can log
    even when things go wrong.
    """
    diag_url = f'{platform_url.rstrip("/")}/api/admin/diagnostics/summary'
    probe = _http_get_json(diag_url, token=token)
    render_state = None
    if render and service_id:
        render_state = render.get_service_status(service_id)
    if probe is None:
        # Probe failure — could be a network blip or the service is down
        return {
            'probe_ok': False,
            'severity': 'error',
            'summary': f'Could not reach diagnostics endpoint at {diag_url}',
            'details': {
                'probe_status': 'unreachable',
                'render_state': (render_state or {}).get('state') if render_state else 'unknown',
            },
        }
    verdict = _classify(probe, render_state)
    return {
        'probe_ok': True,
        'verdict': verdict,
        'probe': probe,
        'render_state': render_state,
    }


# ---------------------------------------------------------------------------
# CLI entry points
# ---------------------------------------------------------------------------

def cmd_check(args: argparse.Namespace) -> int:
    """One-shot check. Exit 0 = healthy, 1 = degraded, 2 = unhealthy."""
    platform_url = args.platform_url or os.getenv('PLATFORM_BASE_URL', '')
    if not platform_url:
        logger.error('PLATFORM_BASE_URL not set and --platform-url not provided')
        return 2
    token = args.token or os.getenv('DEBUG_AGENT_AUTH_TOKEN', '')
    render = RenderClient() if args.use_render else None
    service_id = args.service_id or os.getenv('RENDER_SERVICE_ID', '')
    result = _do_probe(platform_url, token, render, service_id)
    if not result.get('probe_ok'):
        _alert('error', result['summary'], result.get('details', {}))
        return 2
    verdict = result.get('verdict')
    if verdict is None:
        logger.info('OK — platform is healthy')
        return 0
    _alert(verdict['severity'], verdict['summary'], {**verdict.get('details', {}), 'probe': result.get('probe')})
    return {'warning': 1, 'error': 2, 'fatal': 2}.get(verdict['severity'], 1)


def cmd_daemon(args: argparse.Namespace) -> int:
    """
    Long-running daemon. Polls every ``--interval`` seconds, auto-heals
    if ``--auto-heal`` is set and ``DEBUG_AGENT_HEALTH_FAIL_THRESHOLD``
    consecutive failures are observed.
    """
    platform_url = args.platform_url or os.getenv('PLATFORM_BASE_URL', '')
    if not platform_url:
        logger.error('PLATFORM_BASE_URL not set and --platform-url not provided')
        return 2
    token = args.token or os.getenv('DEBUG_AGENT_AUTH_TOKEN', '')
    render = RenderClient()
    service_id = args.service_id or os.getenv('RENDER_SERVICE_ID', '')
    interval = args.interval or int(os.getenv('DEBUG_AGENT_INTERVAL_SEC', '300'))
    auto_heal = args.auto_heal or os.getenv('DEBUG_AGENT_AUTO_HEAL', '').lower() == 'true'
    threshold = int(os.getenv('DEBUG_AGENT_HEALTH_FAIL_THRESHOLD', '3'))
    consecutive_failures = 0
    last_healthy_at = None

    # Graceful shutdown on SIGTERM / SIGINT (Render sends SIGTERM on restart)
    stop_event = threading.Event()
    def _shutdown(signum, frame):
        logger.info(f'received signal {signum}, shutting down')
        stop_event.set()
    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    logger.info(
        f'daemon starting: platform={platform_url} interval={interval}s '
        f'auto_heal={auto_heal} threshold={threshold} render_enabled={render.enabled}'
    )
    while not stop_event.is_set():
        result = _do_probe(platform_url, token, render, service_id)
        if not result.get('probe_ok'):
            consecutive_failures += 1
            _alert('error', result['summary'], result.get('details', {}))
        else:
            verdict = result.get('verdict')
            if verdict is None:
                if last_healthy_at is None or consecutive_failures > 0:
                    logger.info(f'platform healthy at {datetime.now(UTC).isoformat()}Z')
                consecutive_failures = 0
                last_healthy_at = datetime.now(UTC).isoformat() + 'Z'
            else:
                consecutive_failures += 1
                _alert(verdict['severity'], verdict['summary'],
                       {**verdict.get('details', {}), 'consecutive_failures': consecutive_failures})

        # Auto-heal: restart the service if we've failed too many times
        if auto_heal and render.enabled and service_id and consecutive_failures >= threshold:
            logger.warning(f'auto-heal: {consecutive_failures} consecutive failures >= threshold {threshold}, restarting service')
            _alert('warning',
                   f'Auto-heal triggered: {consecutive_failures} consecutive failures',
                   {'service_id': service_id, 'threshold': threshold})
            restart = render.restart_service(service_id)
            if restart is not None:
                # Don't reset consecutive_failures — let the next probe cycle
                # be the source of truth (otherwise we'd report healthy on
                # a half-restarted service)
                pass

        # Sleep with cancellation
        stop_event.wait(interval)
    logger.info('daemon stopped')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='AI Agents debug agent')
    parser.add_argument('--platform-url', help='Base URL of the platform (e.g. https://ai-agents-v10.onrender.com)')
    parser.add_argument('--token', help='JWT for /api/admin/diagnostics (or set DEBUG_AGENT_AUTH_TOKEN)')
    parser.add_argument('--service-id', help='Render service ID (or set RENDER_SERVICE_ID)')
    parser.add_argument('--use-render', action='store_true', help='Cross-reference with Render REST API state')
    sub = parser.add_subparsers(dest='cmd', required=True)
    p_check = sub.add_parser('check', help='One-shot probe')
    p_check.set_defaults(func=cmd_check)
    p_daemon = sub.add_parser('daemon', help='Long-running probe loop')
    p_daemon.add_argument('--interval', type=int, help='Seconds between probes (default: DEBUG_AGENT_INTERVAL_SEC or 300)')
    p_daemon.add_argument('--auto-heal', action='store_true', help='Restart the Render service on sustained failure')
    p_daemon.set_defaults(func=cmd_daemon)
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
