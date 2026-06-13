# F3 deprecation notice — 73M Fontawesome dev-install relocated from `docs/`

**Date:** 2026-06-13
**Followup:** F3 of `ARCHIVE_CLEANUP_TRACKER.md`
**Author:** Claude (cleanup session, branch `cleanup/root-md-cleanup`)
**Scope:** 1 dir move (11,301 files, 73 MB) from `docs/Fontawesome/` → `archive/developer_local_installs/fontawesome_7.1.0/`

---

## What was moved

| From | To | Renamed? | Files | Size |
|---|---|---|---:|---:|
| `docs/Fontawesome/` | `archive/developer_local_installs/fontawesome_7.1.0/` | **YES** (`_7.1.0` suffix) | 11,301 | 73 MB |

The rename adds a `_7.1.0` suffix to preserve the version identity — this
is a specific Fontawesome **7.1.0** install. (The SPA uses **6.7.2 from
CDN**, so the version drift alone is evidence the install was never used
in production — see "Why archive?" below.)

Top-level contents (4 items, all from the Fontawesome 7.1.0 distribution):
- `fontawesome-free-7.1.0-desktop/` — Desktop edition (font files + CSS)
- `fontawesome-free-7.1.0-desktop.zip` — Desktop zip (~32 MB)
- `fontawesome-free-7.1.0-web/` — Web edition (CSS + web fonts)
- `fontawesome-free-7.1.0-web.zip` — Web zip (~33 MB)

## Why archive (not move to `UI/assets/fontawesome/`)?

The F3 row in the tracker (row 46 followup, June 12, 2026) suggested
moving both `docs/icons/` and `docs/Fontawesome/` to `UI/assets/`. The
audit found this needs to be split:

| Asset | Verdict | Reason |
|---|---|---|
| `docs/icons/` (27 SVGs, 128 KB) | → **`UI/assets/icons/`** | Frontend asset — unused stock of Streamline icons the SPA could use in the future. Right place, dormant state. |
| `docs/Fontawesome/` (11,301 files, 73 MB) | → **`archive/developer_local_installs/`** | **NOT a frontend asset the project uses.** It's a developer's local install kit that was checked in by mistake. The SPA never loads from it. The dev-only test HTMLs that *did* reference it are updated to follow the move. |

The deciding evidence:

1. **The SPA loads Fontawesome from CDN, not from `docs/Fontawesome/`.**
   `UI/business-ai-platform-v2.html:366` →
   `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css`
2. **Version drift.** The SPA uses v6.7.2, the local install is v7.1.0.
   If the local install were being used, the icon shapes would have
   visibly changed between v6 and v7 (Fontawesome renames/repaints icons
   across major versions). Nobody noticed because nobody uses the local
   install.
3. **No Flask route serves `docs/Fontawesome/`.** The install is at a
   path Flask doesn't expose, so even if the SPA *did* want to load
   locally, the path would be broken in production.
4. **Only 2 dev-time test HTMLs referenced it** via relative `file://`
   path. Those HTMLs are not loaded by the SPA, not served by Flask, and
   not part of any automated test run — they're dev-only "open this in
   your browser" files.

The cleanest categorization: `docs/icons/` is a **frontend asset the
project doesn't use yet**; `docs/Fontawesome/` is **a developer's local
install that was committed by mistake**. Different categories, different
destinations.

## Inbound-reference audit

A `git grep -lE "docs/[Ff]ontawesome"` against the live repo (excluding
`archive/`, `tmp_row5*`, `docs/archive/`, `*.pyc`) returned exactly 3
files (before this commit):

| File | Context | Action |
|---|---|---|
| `UI/visualisation_engine/test_visualizations.html` | line 16: `<link rel="stylesheet" href="../../docs/Fontawesome/...">` | **Updated in this commit** — path now points at `../../archive/developer_local_installs/fontawesome_7.1.0/...` (the dev test still works) |
| `UI/visualisation_engine/test_visualizations_live.html` | line 14: same | **Updated in this commit** — same path fix |
| `ARCHIVE_CLEANUP_TRACKER.md` | F3 row, this commit resolves it | **Updated in this commit** — F3 marked RESOLVED |

**0 code references** (no `.py` imports, opens, or references this dir).

**0 production references** (no Flask route, no JS module, no CSS
@import references `docs/Fontawesome/` from production code paths).

The 2 test HTMLs are dev-only "open in a browser to run a test suite"
files. They are not loaded by the SPA, not served by Flask (no route
maps `/visualisation_engine/`), and not part of any automated test
runner. They reference a v7.1.0 local install while the SPA uses v6.7.2
CDN — the version drift confirms the test HTMLs are isolated
experiments, not a production dependency.

## Companion move: `docs/icons/` → `UI/assets/icons/`

In the same commit, the 27 SVG icons in `docs/icons/` (128 KB total)
were moved to `UI/assets/icons/`. They are a different category of asset
(stock frontend icons vs. a dev install kit) so they go to a different
destination. See `UI/assets/icons/README.md` for the icon-set
documentation. 0 live references; 0 test HTML references.

## Chain of custody

- **Branch:** `cleanup/root-md-cleanup` (continuation of rows 49/50/51/52
  and F1/F2/F7 followups)
- **Commits:** 1 (this row's commit)
- **Recovery:** `git log --diff-filter=R -- archive/developer_local_installs/`
  (11,301 file moves visible) and `git log --diff-filter=R -- UI/assets/icons/`
  (27 file moves + 1 new README)
- **Predecessor:** row 46 (2026-06-11) flagged F3 in its chain-of-custody
  as a followup
- **Tracker resolution:** F3 marked ~~RESOLVED~~ in followups table

## Related rows

- **Row 46** (2026-06-11, DONE) — flagged F3 in chain-of-custody:
  *"`docs/icons/` (27 SVG/PNG) and `docs/Fontawesome/` (15MB font
  install) are frontend assets misplaced in docs/ — flag for future
  row."* (Note: the actual size is 73 MB, not 15 MB — the row 46
  estimate was off; the audit found the true size.)
- **F1, F2, F4, F5, F7** — sibling followups, all RESOLVED in the same
  cleanup round (June 12-13, 2026)
- **F6** — sibling open followup, low-impact (stale HTML link rot in
  `archive/.../ai_agents_timeline.html`, deferred)

## References

- Tracker followup F3 in `ARCHIVE_CLEANUP_TRACKER.md`
- Findings doc: this file
- Companion icon set README: `UI/assets/icons/README.md`
- Predecessor note: row 46 findings doc / chain-of-custody
- Updated test HTMLs:
  - `UI/visualisation_engine/test_visualizations.html` (line 16)
  - `UI/visualisation_engine/test_visualizations_live.html` (line 14)
- SPA CDN reference (the truth, v6.7.2):
  `UI/business-ai-platform-v2.html:366`
