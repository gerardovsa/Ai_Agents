"""
Startup Phase Timing Instrumentation
====================================

Stdlib-only helper that records named startup phases in an in-memory list
and exposes them via two diagnostic endpoints:

- GET /api/diagnostics/startup       (JSON)
- GET /api/diagnostics/startup.txt   (plain text)

The helper is intentionally additive and dependency-free:

- No imports from this package (only stdlib: time, threading, os, json,
  dataclasses, datetime).
- No logging infrastructure calls (so it cannot recurse into the very code
  paths it is measuring).
- All stdout writes go through a module-level threading.Lock so the
  connection-leak-detector's prewarm thread cannot interleave lines.

The module also prints a one-line summary to stdout for each phase as a
secondary fallback (use STARTUP_TIMING=0 to silence). On Render the stdout
lines and the endpoint serve the same purpose from different angles:

- Endpoint is the primary surface (no log scraping required).
- Stdout line is the fallback when the worker is up but the endpoint is
  unreachable (e.g. the load balancer has not yet routed traffic).

Phase taxonomy (flask_app.py anchors):
    1.  bootstrap_logging
    2.  framework_config
    3.  core_route_imports
    4.  flask_app_create
    5.  database_initialization
    6.  module_registry_initialization
    7.  blueprint_registration
    8.  module_blueprint_autoload
    9.  socketio_services
    10. scheduler_and_finalization
    11. gunicorn_runtime_services
    12. module_import_complete

Usage (from flask_app.py):

    from shared.startup_timing import begin, end
    begin('bootstrap_logging')
    ... logger setup ...
    end('bootstrap_logging')

Environment variables:
    STARTUP_TIMING       '0' disables all output (default: enabled)
    STARTUP_TIMING_QUIET '1' disables stdout writes but keeps in-memory
                         records so /api/diagnostics/startup still works.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ============================================================================
# Module-level state — self-anchored at import time
# ============================================================================
# perf_counter() is monotonic and immune to wall-clock adjustments; all dt
# deltas are computed against _BOOT_T0. _WALL_T0 is only used to render an
# ISO-8601 wall timestamp for the first record.
_BOOT_T0: float = time.perf_counter()
_WALL_T0: float = time.time()

_RECORDS: List["PhaseRecord"] = []
_LOCK: threading.Lock = threading.Lock()
_OPEN: Dict[str, float] = {}  # phase_id -> perf_counter at begin()

# 5 second target — Render healthCheckPath timeout.
RENDER_HEALTHCHECK_BUDGET_MS: float = 5000.0


# ============================================================================
# PhaseRecord
# ============================================================================
@dataclass
class PhaseRecord:
    """One phase of the boot sequence."""

    id: str
    status: str  # 'ok' | 'error'
    dt_ms: float
    total_ms: float
    wall: str  # ISO-8601 UTC
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# Configuration
# ============================================================================
def _stdout_enabled() -> bool:
    """Whether to emit a one-line [STARTUP_TIMING] line per phase."""
    if os.environ.get("STARTUP_TIMING_QUIET", "").strip() == "1":
        return False
    if os.environ.get("STARTUP_TIMING", "").strip() == "0":
        return False
    return True


def is_enabled() -> bool:
    """True unless STARTUP_TIMING=0."""
    return os.environ.get("STARTUP_TIMING", "").strip() != "0"


def configure_from_shell() -> None:
    """No-op stub for symmetry with future per-phase gating.

    Currently parses STARTUP_TIMING and STARTUP_TIMING_QUIET as side
    effects of subsequent calls. Kept so callers can wire per-phase
    filters later without changing the call site.
    """
    return None


def get_boot_t0() -> float:
    """Return the perf_counter anchor used for all dt calculations."""
    return _BOOT_T0


def get_wall_t0() -> float:
    """Return the wall-clock anchor used for ISO timestamps."""
    return _WALL_T0


# ============================================================================
# Note sanitization
# ============================================================================
_NOTE_MAX = 80


def _sanitize_note(note: str) -> str:
    """Strip non-ASCII bytes and truncate to NOTE_MAX chars.

    The endpoint exposes notes verbatim, so we must guarantee the response
    is JSON-safe and the stdout line is greppable from any terminal.
    """
    if not note:
        return ""
    try:
        ascii_safe = note.encode("ascii", "replace").decode("ascii")
    except Exception:
        ascii_safe = ""
    if len(ascii_safe) > _NOTE_MAX:
        ascii_safe = ascii_safe[: _NOTE_MAX - 3] + "..."
    return ascii_safe


def _iso_utc_from_perf(perf_value: float) -> str:
    """Convert a perf_counter value to an ISO-8601 UTC timestamp."""
    wall = _WALL_T0 + (perf_value - _BOOT_T0)
    return datetime.fromtimestamp(wall, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ============================================================================
# Phase API
# ============================================================================
def begin(phase_id: str, note: str = "") -> None:
    """Start timing a phase. Pairs with end(phase_id)."""
    if not is_enabled():
        return
    clean_note = _sanitize_note(note)
    with _LOCK:
        _OPEN[phase_id] = time.perf_counter()


def end(phase_id: str, note: str = "", status: str = "ok") -> None:
    """Finish timing a phase and record it.

    If begin() was not called for phase_id, the delta is measured from
    _BOOT_T0 so the record is still meaningful (rather than dropped).
    """
    if not is_enabled():
        return
    end_perf = time.perf_counter()
    start_perf: Optional[float] = None
    with _LOCK:
        start_perf = _OPEN.pop(phase_id, None)
        if start_perf is None:
            start_perf = _BOOT_T0
        dt_ms = (end_perf - start_perf) * 1000.0
        total_ms = (end_perf - _BOOT_T0) * 1000.0
        record = PhaseRecord(
            id=phase_id,
            status=status,
            dt_ms=round(dt_ms, 3),
            total_ms=round(total_ms, 3),
            wall=_iso_utc_from_perf(end_perf),
            note=_sanitize_note(note),
        )
        _RECORDS.append(record)
    _emit_stdout(record)


def mark(phase_id: str, note: str = "") -> None:
    """Record an instant event with dt_ms=0.

    Useful for greenlet/sync ops that cannot be bracketed with begin/end.
    """
    if not is_enabled():
        return
    end_perf = time.perf_counter()
    with _LOCK:
        total_ms = (end_perf - _BOOT_T0) * 1000.0
        record = PhaseRecord(
            id=phase_id,
            status="ok",
            dt_ms=0.0,
            total_ms=round(total_ms, 3),
            wall=_iso_utc_from_perf(end_perf),
            note=_sanitize_note(note),
        )
        _RECORDS.append(record)
    _emit_stdout(record)


def _emit_stdout(record: PhaseRecord) -> None:
    """Emit one greppable line to stdout under the lock.

    Format is intentionally simple and stable; do not embed emojis or
    unicode bullets in note (sanitized upstream).
    """
    if not _stdout_enabled():
        return
    line = (
        "[STARTUP_TIMING] phase={id} status={status} "
        "dt_ms={dt_ms} total_ms={total_ms} wall={wall} note=\"{note}\""
    ).format(
        id=record.id,
        status=record.status,
        dt_ms=record.dt_ms,
        total_ms=record.total_ms,
        wall=record.wall,
        note=record.note,
    )
    try:
        with _LOCK:
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
    except Exception:
        # A broken stdout must never break boot.
        pass


# ============================================================================
# Snapshot / summary / render — consumed by the diagnostic endpoints
# ============================================================================
def snapshot() -> Dict[str, Any]:
    """JSON-serialisable snapshot of all records collected so far."""
    with _LOCK:
        records = [r.to_dict() for r in _RECORDS]
    boot_total_ms = records[-1]["total_ms"] if records else 0.0
    return {
        "ok": True,
        "pid": os.getpid(),
        "render_mode": os.environ.get("RENDER", "").lower() == "true",
        "boot_t0_wall": _iso_utc_from_perf(_BOOT_T0),
        "boot_total_ms": round(boot_total_ms, 3),
        "phases": records,
        "summary": _compute_summary(records),
    }


def _compute_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pick the slowest phase and decide whether we are under Render's 5s budget."""
    if not records:
        return {
            "slowest_phase": None,
            "second_slowest": None,
            "under_5s_target": True,
            "phases_over_1000ms": 0,
        }
    by_dt = sorted(records, key=lambda r: r["dt_ms"], reverse=True)
    slowest = by_dt[0]
    second = by_dt[1] if len(by_dt) > 1 else None
    total = records[-1]["total_ms"]
    return {
        "slowest_phase": {"id": slowest["id"], "dt_ms": slowest["dt_ms"]},
        "second_slowest": (
            {"id": second["id"], "dt_ms": second["dt_ms"]} if second else None
        ),
        "under_5s_target": total < RENDER_HEALTHCHECK_BUDGET_MS,
        "phases_over_1000ms": sum(1 for r in records if r["dt_ms"] >= 1000.0),
    }


def summary() -> Dict[str, Any]:
    """Return just the summary block (lightweight for /api/health/detailed)."""
    return snapshot()["summary"]


def render_text() -> str:
    """Plain-text tabular report (curl | less friendly)."""
    snap = snapshot()
    phases = snap["phases"]
    lines: List[str] = []
    lines.append("PHASE                              STATUS    DT_MS     TOTAL_MS   WALL (UTC)")
    lines.append("-" * 90)
    for r in phases:
        lines.append(
            "{id:<33} {status:<8} {dt_ms:>8.1f}  {total_ms:>10.1f}   {wall}".format(
                id=r["id"][:33],
                status=r["status"],
                dt_ms=r["dt_ms"],
                total_ms=r["total_ms"],
                wall=r["wall"],
            )
        )
    lines.append("-" * 90)
    total = snap["boot_total_ms"]
    lines.append(
        "TOTAL BOOT                                              {total:>10.1f} ms (~{sec:.1f}s)".format(
            total=total, sec=total / 1000.0
        )
    )
    s = snap["summary"]
    if s["slowest_phase"]:
        lines.append(
            "SLOWEST: {id} ({dt_ms:.1f} ms)".format(
                id=s["slowest_phase"]["id"], dt_ms=s["slowest_phase"]["dt_ms"]
            )
        )
    lines.append("UNDER_5S_TARGET: {ok}".format(ok=str(s["under_5s_target"])))
    return "\n".join(lines) + "\n"


def render_json() -> str:
    """Pre-formatted JSON snapshot — preferred over snapshot() in endpoints
    so callers cannot accidentally forget json.dumps.
    """
    return json.dumps(snapshot(), indent=2, sort_keys=False)


# ============================================================================
# Reset (used only by tests)
# ============================================================================
def _reset_for_tests() -> None:
    """Wipe all records and re-anchor. Tests only."""
    global _BOOT_T0, _WALL_T0
    with _LOCK:
        _RECORDS.clear()
        _OPEN.clear()
    _BOOT_T0 = time.perf_counter()
    _WALL_T0 = time.time()


__all__ = [
    "PhaseRecord",
    "RENDER_HEALTHCHECK_BUDGET_MS",
    "begin",
    "configure_from_shell",
    "end",
    "get_boot_t0",
    "get_wall_t0",
    "is_enabled",
    "mark",
    "render_json",
    "render_text",
    "snapshot",
    "summary",
    "_reset_for_tests",
]