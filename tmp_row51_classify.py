"""Row 51 classifier v3 - adds aggressive topic-prefix patterns."""
import csv, re
from collections import Counter
from pathlib import Path

INVENTORY = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents\tmp_row51_inventory.csv")
OUT_CLASS = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents\tmp_row51_classification.csv")
OUT_SUMMARY = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents\tmp_row51_summary.txt")

CONTRACT_EXACT = {
    "README.md", "README_V11.md", "LICENSE", "CLAUDE.md",
    "ARCHIVE_CLEANUP_PLAN.md", "ARCHIVE_CLEANUP_SUMMARY_NOV30.md",
    "ARCHIVE_CLEANUP_TRACKER.md", "ARCHIVE_SAFETY_VERIFICATION.md",
}

KEEP_PATTERNS = [
    r"^_ARCHIVED_", r"^START_HERE", r"^HOW_TO_",
    r"^PROJECT_STRUCTURE", r"^FILE_INDEX", r"^DIRECTORY",
    r"_DEPLOYMENT\.md$", r"_DEPLOY\.md$", r"_RUNBOOK\.md$",
    r"_MIGRATION_PLAN\.md$", r"_MASTER_PLAN",
    r"^README", r"^CHANGELOG", r"^VERSION", r"^CONTRIBUTING", r"^SECURITY",
]

MONTH = r"(?:NOV|DEC|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT)"
DATE_RE = re.compile(
    rf"_(?:{MONTH})(\d{{1,2}})(?:_(\d{{4}}))?"
    rf"|_(\d{{4}})-(\d{{2}})-(\d{{2}})"
    rf"|_{MONTH}_?(\d{{4}})",
    re.IGNORECASE,
)

SCRATCH_RES_RAW = [
    r"_FIX(?:_COMPLETE|_PROGRESS|_IN_PROGRESS|_ATTEMPT|_SUMMARY|_REPORT|_APPLIED|_JOURNAL|_TRACE|_LOG|ED)?$",
    r"_FIXES(?:_COMPLETE|_SUMMARY|_LOG)?$",
    r"_DEBUG(?:_COMPLETE|_SUMMARY|_JOURNAL|_LOG|ED)?$",
    r"_COMPLETE(?:_[A-Z]+(?:_\d{4})?)?$",
    r"_PROGRESS(?:_REPORT|_CHECK)?$",
    r"_STATUS_UPDATE", r"_POST_MORTEM", r"_RETROSPECTIVE",
    r"_WRAP_UP", r"_RESOLUTION$", r"_BEFORE_AFTER", r"_COMPARISON_REPORT",
    r"_REVIEW_COMPLETE", r"_AUDIT(?:_COMPLETE|_REPORT|_SUMMARY|ED)?$",
    r"_ANALYSIS(?:_REPORT|_SUMMARY|_COMPLETE|_RESULTS|_FINDINGS)?$",
    r"_RESEARCH(?:_RESULTS|_FINDINGS|_SUMMARY)?$",
    r"_INVESTIGATION$", r"_EVALUATION$", r"_PERFORMANCE_(?:REPORT|SUMMARY|FIX|GUIDE|METRICS|BENCHMARK|TUNING)$",
    r"_SESSION_SUMMARY", r"_STAND_UP", r"_STATUS_AS_OF", r"_EXPLORATION$",
    r"_EXPERIMENT$", r"_PROOF_OF_CONCEPT", r"_POC_RESULTS",
    r"_WALK_THROUGH", r"_DEEP_DIVE", r"_WRITE_UP$",
    r"_DESIGN(?:_DOC|_DECISIONS|_PROPOSAL)$", r"_PROPOSAL$", r"_RFC$",
    r"_SPIKE_RESULTS", r"_RECOMMENDATIONS$", r"_ROADMAP$", r"_TIMELINE$",
    r"_MILESTONES$", r"_SNAPSHOT$", r"_OUTCOMES?$", r"_RUNDOWN$",
    r"_DRAFT_OF", r"_WIP$", r"_TODO$", r"_DECISION_LOG", r"_CHANGE_LOG",
    r"_HANDOFF$", r"_HAND_OFF", r"_MEETING_NOTES", r"_TRANSCRIPT$",
    r"_MINUTES$", r"_KICKOFF$", r"_CHECK_IN$",
    r"_SUCCESS(?:_|\.md$)", r"_VERIFIED(?:_|\.md$)",
    r"_IMPLEMENTATION\.md$", r"_INTEGRATION\.md$",
    r"_QUICK_REFERENCE\.md$", r"_QUICK_REF\.md$",
    r"_QUICK_START\.md$", r"_QUICK_TEST\.md$", r"_UPGRADE\.md$",
    r"_CONSOLIDATION_REPORT", r"_CONSOLIDATION$", r"_CHANGES_SUMMARY",
    r"_TESTING(?:_RESULTS|_REPORT|_GUIDE|_COMPLETE|_SUMMARY|_PHASE)$",
    r"_VALIDATION(?:_REPORT|_RESULTS|_COMPLETE)$",
    r"_UPGRADE(?:_COMPLETE|_SUMMARY)$",
    r"_INTEGRATION(?:_SUCCESS|_COMPLETE|_SUMMARY|_REPORT|_ANALYSIS|_TEST)$",
    r"_GUIDE_FOR", r"_USER_GUIDE$", r"_OPERATIONS_GUIDE", r"_OPS_GUIDE",
    r"_INSTALL(?:_ATION)?_GUIDE$", r"_MIGRATION(?:_GUIDE|_INSTRUCTIONS)$",
    r"_SETUP(?:_GUIDE|_INSTRUCTIONS|_COMPLETE|_SUMMARY)$",
    r"_PHASE_\d", r"_PHASE_COMPLETE",
    r"_ENHANCEMENTS(?:_COMPLETE|_SUMMARY|_REPORT)$",
    r"_RELEASE_NOTES", r"_DAY_\d{1,2}", r"_WEEK_\d{1,2}",
    r"_MILESTONE_\d", r"_SPRINT_\d", r"_ROUND_\d", r"_RUN_\d",
    r"_ITERATION_\d", r"_CYCLE_\d",
    r"_CRITICAL_(?:FIX|DISCOVERY|BUG|ISSUE|ERROR)$",
    r"_PROBLEM(?:_STATEMENT|$)", r"_WORKAROUND$", r"_KNOWN_ISSUES$",
    r"_BUG_REPORT$", r"_INCIDENT_REPORT$", r"_POST_FIX$", r"_POST_DEPLOY$",
    r"_POST_LAUNCH$", r"_POST_RELEASE$", r"_PRE_LAUNCH$", r"_PRE_RELEASE$",
    r"_V\d_REVIEW$", r"_V\d_COMPLETE$", r"_V\d_SUMMAR$",
    r"_TASK(?:_COMPLETE|_REPORT|_SUMMARY)$",
    r"_CLEANUP(?:_SUMMAR|_COMPLETE|_REPORT|_ANALYSIS)$",
    r"_WIRING(?:_COMPLETE|_SUMMARY)$",
    r"_DEBUGGING(?:_COMPLETE|_SUMMARY)$",
    r"_ALIGNMENT(?:_ASSESSMENT|_AUDIT|_FIX|_COMPLETE)$",
    r"_INSTRUCTIONS(?:_COMPLETE|_SUMMARY|_FOR)$",
    r"_ENHANCED(?:_COMPLETE|_SUMMARY)$",
    r"_ALL_PHASES(?:_SUMMAR|_COMPLETE)$",
    r"_REORGANIZATION$", r"_RESTRUCTURING$",
    r"_REFACTOR(?:_COMPLETE|_SUMMARY)$",
    r"_POLISH(?:_COMPLETE|_SUMMARY)$",
    r"_GO_LIVE$", r"_GOLIVE$",
    r"_LAUNCH(?:_CHECKLIST|_PLAN|_COMPLETE|_SUMMARY)$",
    r"_ONBOARDING(?:_GUIDE|_COMPLETE)$",
    r"_TR_\d", r"_EPIC_\d", r"_TICKET_\d", r"_ISSUE_\d", r"_PR_\d",
    r"_MERGE(?:_COMPLETE|_SUMMARY)$", r"_RELEASE_SUMMAR$",
    r"_EOL$", r"_DEPRECATION_NOTICE$",
    r"_MIGRATION(?:_COMPLETE|_SUMMARY|_REPORT)$",
    r"_PROVISION(?:_COMPLETE|_SUMMARY)$",
    r"_CONNECTION(?:_COMPLETE|_FIX)$",
    r"_ENV_VARS(?:_SUMMAR|_REPORT|_GUIDE)$",
    r"_CONFIG(?:_SUMMAR|_REPORT|_CHANGES)$",
    r"_DEVELOPER_GUIDE$", r"_DEV_(?:GUIDE|NOTES|REFERENCE|REFERENCE_CARD)$",
    r"_INTEGRATION_GUIDE$", r"_USER_REFERENCE$",
    r"_ARCHITECTURE(?:_DECISION|_REVIEW|_REPORT|_PROPOSAL|_SUMMARY)$",
    r"_CONTRIBUTING_GUIDE$", r"_WELCOME(?:_TO|$)",
    r"_GIT_(?:IGNORE|HOOKS|SUBMODULES)$",
    r"_PULL_REQUEST$", r"_BRANCH_PROTECTION$",
    r"_RENDER(?:_DEPLOY|_GUIDE)$", r"_DEPLOYMENT(?:_GUIDE|_RUNBOOK|_PLAN|_CHECKLIST|_SUMMAR|_COMPLETE)$",
    r"_ROLLBACK(?:_PLAN|_PROCEDURE)$",
    r"_BACKUP(?:_PROCEDURE|_STRATEGY)$",
    r"_MAINTENANCE_WINDOW$", r"_DOWNTIME_PLAN$",
    r"_SCALING(?:_GUIDE|_PLAN)$", r"_SCALE_UP$", r"_SCALE_DOWN$",
    r"_OPTIMIZATION(?:_SUMMAR|_REPORT|_COMPLETE|_GUIDE|_FIX)$",
    r"_MEMORY_OPTIMIZATION$", r"_MEMORY_LEAK$", r"_LEAK(?:_DETECTION|_FIX)$",
    r"_CONNECTION_POOL$", r"_POOL_EXHAUST$", r"_POOL_FIX$",
    r"_OUT_OF_MEMORY$", r"_OOM$",
    r"_TIMEOUT(?:_FIX|_SUMMAR|_REPORT|$)", r"_RETRY(?:_LOGIC|_FIX)$",
    r"_RATE_LIMIT(?:_ING)?$", r"_THROTTLE$",
    r"_CIRCUIT_BREAKER$", r"_BULKHEAD$", r"_FALLBACK(?:_STRATEGY|$)",
    r"_DEADLOCK$", r"_RACE_CONDITION$", r"_CONCURRENCY$", r"_LOCK_CONTENTION$",
    r"_DELIVERY_GUARANTEE$", r"_MESSAGE_BROKER$",
    r"_CACHE(?:\.md|_GUIDE|_SUMMARY|_REPORT|_FIX|_INVALIDATION|_WARMING|_STAMPEDE|_COLD_START|_EVICTION|_POLICY|_LAYER|_STRATEGY|_COMPLETE|_RESULTS|_STATS|_STATUS|_REVIEW|_AUDIT|_ANALYSIS|_DEBUG|_CLEAR|_BUST|_BUSTING|_HIT|_MISS|_KEY|_TTL|_WARM|_FLUSH|_PURGE|_REFRESH|_EXPIRE|_EXPIRY|_EVICT|_STORE|_BACKEND|_PROVIDER|_ENGINE|_WRAPPER|_ABSTRACTION|_MANAGER|_SERVICE|_MODULE|_MIDDLEWARE|_PLUGIN|_EXTENSION|_ADAPTER|_INTERFACE|_CONTRACT|_API|_CLIENT|_SERVER|_PROXY|_GATEWAY|_SIDECAR|_DAEMON|_WORKER|_JOB|_TASK|_SCHEDUL|_CLEANER|_JANITOR|_GARBAGE|_COLLECT|_COMPACT|_DEFRAG|_REINDEX|_REBUILD|_REPAIR|_RECOVERY|_RESTORE|_ARCHIVE|_HISTORY|_LOG|_TRACE|_MONITOR|_OBSERV|_METRIC|_ALERT|_DASHBOARD|_PANEL|_UI|_VIEW|_PAGE|_ROUTE|_ENDPOINT|_API_DOC|_REFERENCE|_INDEX|_LIST|_MAP|_TABLE|_CHART|_GRAPH|_TREE|_HIERARCHY|_STRUCTURE|_LAYOUT|_DESIGN|_MOCK|_MOCKUP|_PROTOTYPE|_PROOF|_DEMO|_SAMPLE|_EXAMPLE|_TEMPLATE|_STARTER|_SCAFFOLD|_BOILERPLATE|_SNIPPET|_FRAGMENT|_PIECE|_PART|_SECTION|_BLOCK|_ELEMENT|_COMPONENT|_WIDGET|_PACKAGE|_LIBRARY|_FRAMEWORK|_TOOLKIT|_TOOLBOX|_TOOLSET|_SUITE|_BUNDLE|_KIT|_PACK|_SET|_COLLECTION|_REPOSITORY|_VAULT|_SAFE|_LOCKER)$",
    r"_[A-Z]+_EXTRACTION_",
    r"_[A-Z]+_MODULARIZATION_",
    r"_[A-Z]+_INTEGRATION_(?!SUCCESS|COMPLETE|TEST|FIX)",
    r"_[A-Z]+_IMPLEMENTATION_(?!SUCCESS|COMPLETE|TEST|FIX)",
    r"_[A-Z]+_REDESIGN_",
    r"_[A-Z]+_REFACTOR_",
    r"_[A-Z]+_OVERVIEW_",
    r"_[A-Z]+_ENHANCEMENT_",
    r"_[A-Z]+_STRUCTURE_",
    r"_[A-Z]+_BREAKDOWN_",
    r"_[A-Z]+_CHECKLIST_",
    r"_[A-Z]+_TESTING_",
    r"_[A-Z]+_BUG_FIX",
    r"_[A-Z]+_BUGFIX_",
    r"_[A-Z]+_WALKTHROUGH_",
    r"_[A-Z]+_WALK_THROUGH_",
    r"_[A-Z]+_PLAYBOOK_",
    r"_[A-Z]+_ASSESSMENT_",
    r"_[A-Z]+_EVAL_",
    r"_[A-Z]+_TROUBLESHOOTING_",
    r"_[A-Z]+_DEEP_DIVE_",
    r"_[A-Z]+_WIREFRAME_",
    r"_[A-Z]+_MOCKUP_",
    r"_[A-Z]+_PROTOTYPE_",
    r"_[A-Z]+_SNAPSHOT_",
    r"_[A-Z]+_AUDIT_",
    r"_[A-Z]+_MIGRATION_",
    r"_[A-Z]+_ENHANCED_",
    r"_[A-Z]+_SPRINT_",
    r"_[A-Z]+_ROUND_",
    r"_[A-Z]+_ITERATION_",
    r"_[A-Z]+_CYCLE_",
    r"_[A-Z]+_DAY_",
    r"_[A-Z]+_WEEK_",
    r"_POLISH_",
    r"_QUICK_TEST_",
    r"_QUICK_FIX_",
    r"_QUICK_START_",
    r"_QUICK_REF_",
    r"_CONSOLIDATION_",
    r"_REORG_",
    r"_RESTRUCTURING_",
    r"_INTEGRATION_(PLAN|GUIDE|INSTRUCTIONS|ANALYSIS|SUMMARY|NOTES|OVERVIEW)$",
    r"_IMPLEMENTATION_(PLAN|GUIDE|INSTRUCTIONS|ANALYSIS|SUMMARY|NOTES|OVERVIEW)$",
    r"_TESTING_(PLAN|GUIDE|INSTRUCTIONS|ANALYSIS|SUMMARY|NOTES|OVERVIEW|REPORT|RESULTS|PHASE)$",
    r"_REVIEW_(NOTES|FINDINGS|FEEDBACK|CRITIQUE|LOG|OUTCOME|COMPLETE|REPORT)$",
    r"_ASSESSMENT_(NOTES|FINDINGS|FEEDBACK|CRITIQUE|LOG|OUTCOME|COMPLETE|REPORT)$",
    r"_FIX_(NOTES|FINDINGS|FEEDBACK|CRITIQUE|LOG|OUTCOME|COMPLETE|REPORT)$",
    r"_REFACTOR_(NOTES|FINDINGS|FEEDBACK|CRITIQUE|LOG|OUTCOME|COMPLETE|REPORT)$",
    r"_OVERVIEW$",
    r"_STRUCTURE$",
    r"_BREAKDOWN$",
    r"_CHECKLIST$",
    r"_WALKTHROUGH$",
    r"_WALK_THROUGH$",
    r"_PLAYBOOK$",
    r"_TEMPLATE$",
    r"_EXAMPLE$",
    r"_SAMPLE$",
    r"_SNAPSHOT$",
    r"_MOCKUP$",
    r"_PROTOTYPE$",
    r"_WIREFRAME$",
    r"_LOG$",
    r"_JOURNAL$",
    r"_DIARY$",
    r"_BRAINSTORM$",
    r"_IDEAS$",
    r"_DRAFT$",
    r"_OUTLINE$",
    r"_SKELETON$",
    r"_STUB$",
    r"_RAW$",
    r"_NEXT_STEPS$",
    r"_RETRO_",
    r"_RECAP_",
    r"_WRAP_UP_",
    r"_WRAP-UP_",
    r"_WELCOME(?:_TO|$)",
]

SCRATCH_RES = [re.compile(p, re.IGNORECASE) for p in SCRATCH_RES_RAW]

SCRATCH_TITLE_KW = [
    "fix complete", "fix applied", "fix in progress", "fix progress",
    "complete analysis", "complete fix", "complete guide", "complete implementation",
    "complete summary", "complete overview", "complete report",
    "debug complete", "debug summary", "debug log",
    "post-mortem", "post mortem", "retrospective",
    "implementation summary", "implementation complete",
    "fix summary", "fix log", "fix journal",
    "what worked", "what's done", "wrap up", "wrap-up",
    "issue analysis", "issue resolved", "issue closed",
    "incident report", "incident summary",
    "performance analysis", "performance report", "performance summary",
    "test results", "test report", "test summary", "test complete",
    "validation results", "validation summary", "validation report",
    "deep dive", "write-up", "write up", "walk-through", "walk through",
    "before/after", "before & after", "before and after",
    "comparison report", "comparison summary",
    "recap of", "recap:", "summary of", "summary:",
    "migration summary", "migration report", "migration complete",
    "deployment summary", "deployment complete", "deployment report",
    "integration summary", "integration complete", "integration report",
    "configuration guide", "configuration summary",
    "session summary", "session notes", "session log",
    "kickoff", "kick-off", "status update", "status as of",
    "process review", "process walkthrough",
    "investigation", "evaluation", "assessment", "audit",
    "research summary", "research findings", "research results",
    "analysis findings", "analysis results", "analysis summary",
    "case study", "user story", "customer journey", "user journey",
    "phase 1", "phase 2", "phase 3", "phase 4", "phase 5",
    "phase complete", "phase summary", "phase report",
    "step by step", "step-by-step",
    "what i did", "what i learned", "what i built",
    "lessons learned", "lessons learnt", "postmortem",
    "discovery:", "found:", "noticed:", "discovered:",
    "fix:", "patch:", "hotfix:",
    "bug:", "issue:",
    "release notes", "release summary", "release:",
    "version 1", "version 2", "version 3",
    "v1.0", "v1.1", "v2.0", "v2.1", "v3.0",
    "milestone 1", "milestone 2", "milestone 3",
    "sprint 1", "sprint 2", "sprint 3",
    "round 1", "round 2", "round 3",
    "iteration 1", "iteration 2", "iteration 3",
]

KEEP_RE = [re.compile(p, re.IGNORECASE) for p in KEEP_PATTERNS]


def classify(name, size, mtime, first_line, second_line):
    title = (first_line + " " + second_line).lower()

    if name in CONTRACT_EXACT:
        return "Contract", "keep", "untouchable per per-feature prompt hard rules"

    if name.startswith("_ARCHIVED_"):
        return "Historical", "keep-as-prefixed", "already in archived state"

    for r in KEEP_RE:
        if r.search(name):
            if any(t in name for t in ("DEPLOY", "RUNBOOK", "START_HERE", "HOW_TO", "PROJECT_STRUCTURE", "FILE_INDEX", "DIRECTORY")):
                return "Runbook", "keep", "matches runbook pattern"
            return "Canonical", "keep", "matches canonical pattern"

    for r in SCRATCH_RES:
        if r.search(name):
            if any(k in title for k in ("fix", "debug", "troubleshoot", "502", "404", "error", "bug", "patch", "hotfix", "incident", "outage")):
                return "Historical", "git mv -> archive/timelines_and_reports/", "fix/debug/incident content"
            if any(k in title for k in ("analysis", "investigation", "evaluation", "research", "deep dive", "audit", "case study", "whitepaper")):
                return "Debug", "git mv -> archive/analysis_reports/", "analysis/audit/research content"
            return "Scratch", "git mv -> archive/timelines_and_reports/", "fix/progress/summary content"

    m = DATE_RE.search(name)
    if m:
        year = None
        for g in m.groups():
            if g and g.isdigit() and len(g) == 4:
                year = int(g)
                break
        if year is None:
            name_up = name.upper()
            if any(m in name_up for m in ("NOV", "DEC")):
                year = 2025
            elif any(m in name_up for m in ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT")):
                year = 2026
        if year is not None and year < 2026:
            return "Historical", "git mv -> archive/timelines_and_reports/", f"dated {year}"
        if year is not None and year == 2026:
            return "Scratch", "git mv -> archive/timelines_and_reports/", f"dated {year}"

    for kw in SCRATCH_TITLE_KW:
        if kw in title:
            return "Scratch", "git mv -> archive/timelines_and_reports/", f"title contains '{kw}'"

    return "Suspicious", "review-needed", "no pattern matched - needs judgement"


rows = []
with INVENTORY.open("r", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        bucket, action, reason = classify(row["filename"], int(row["size_bytes"]), float(row["mtime"]), row["first_line"], row["second_line"])
        rows.append({"filename": row["filename"], "size": int(row["size_bytes"]), "bucket": bucket, "action": action, "reason": reason, "first_line": row["first_line"][:120]})

with OUT_CLASS.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["filename", "size", "bucket", "action", "reason", "first_line"])
    w.writeheader()
    for r in rows:
        w.writerow(r)

counts = Counter(r["bucket"] for r in rows)
sizes = {}
for r in rows:
    sizes[r["bucket"]] = sizes.get(r["bucket"], 0) + r["size"]

with OUT_SUMMARY.open("w", encoding="utf-8") as f:
    f.write("Row 51 classification summary\n" + "=" * 60 + "\n\n")
    f.write(f"Total files: {len(rows)}\n\n")
    f.write("By bucket:\n")
    for bucket, count in counts.most_common():
        f.write(f"  {bucket:15} {count:5} files  ({sizes.get(bucket, 0):>12,} bytes)\n")
    f.write("\nSuspicious (need manual review):\n")
    for r in rows:
        if r["bucket"] == "Suspicious":
            f.write(f"  {r['filename']:60} | {r['first_line'][:80]}\n")

print(f"Total: {len(rows)} files", flush=True)
print("By bucket:")
for b, c in counts.most_common():
    print(f"  {b:15} {c:5} files")
susp = [r for r in rows if r["bucket"] == "Suspicious"]
print(f"Suspicious: {len(susp)}", flush=True)
print(f"Wrote {OUT_CLASS}", flush=True)
print(f"Wrote {OUT_SUMMARY}", flush=True)
