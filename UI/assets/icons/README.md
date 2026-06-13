# UI assets — icons

**27 Streamline SVG icons** relocated from `docs/icons/` on **2026-06-13**
(F3 of `ARCHIVE_CLEANUP_TRACKER.md`).

## What's here

| Count | Source | Naming convention |
|---:|---|---|
| ~12 | Streamline Carbon | `Icon-Name--Streamline-Carbon.svg` |
| ~10 | Streamline Ultimate | `Icon-Name--Streamline-Ultimate.svg` |
| ~5 | Streamline Simple Icons | `Icon-Name--Streamline-Simple-Icons.svg` |

Examples: `Column-Delete--Streamline-Carbon.svg`, `Folder-Add--Streamline-Ultimate.svg`,
`Grapheneos--Streamline-Simple-Icons.svg`, `Messages-People-User-Check--Streamline-Ultimate.svg`.

## Status

**Unused by the SPA at present.** The main SPA (`UI/business-ai-platform-v2.html`)
uses Fontawesome from CDN (v6.7.2 from cdnjs.cloudflare.com, per CLAUDE.md §12
"Design system"). These 27 SVGs are a stockpile of stock icons that could
be used by the SPA in the future — they are not dead code, just dormant.

## How to use

The SPA doesn't currently serve from `UI/assets/`. To use any of these icons
you have two options:

1. **Inline them** — copy the SVG body into your HTML. Smallest payload,
   loses the ability to style with CSS classes.
2. **Serve them** — add a Flask static route for `/assets/<path>` and load
   via `<img src="/assets/icons/...">` or `<use href="...">` from a sprite
   sheet. The dir is now in the right place (`UI/assets/icons/`), so
   adding the route is a one-line Flask change.

## Why not in `docs/icons/`

The `docs/` directory is for **long-form reference material** (CLAUDE.md
§2 — "Where documentation lives"). SVG icons are **runtime frontend
assets**, not documentation. Putting them in `docs/` violated the
"single responsibility per top-level directory" rule. F3 fixed this.

## References

- `archive/timelines_and_reports/DEPRECATION_NOTICE_F3.md` — chain of
  custody for the move
- `.github/copilot-instructions.md` §5 — file map
- CLAUDE.md §12 — design system
