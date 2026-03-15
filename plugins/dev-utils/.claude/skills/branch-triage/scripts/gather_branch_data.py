#!/usr/bin/env python3
"""Gather git branch data and generate an AI prompt for triage analysis.

Standalone script — no external dependencies. Works in any git repo.
Outputs a prompt that asks the AI to respond with JSON conforming to the
dashboard template schema. The JSON can then be pasted into template.html.

Usage:
    python3 gather_branch_data.py              # Print prompt to stdout
    python3 gather_branch_data.py --copy       # Also copy to clipboard
    python3 gather_branch_data.py --parallel 8 # Control parallelism
"""

from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(cmd: str, timeout: int = 30) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return ""


def _run_lines(cmd: str) -> list[str]:
    out = _run(cmd)
    return [line for line in out.splitlines() if line.strip()] if out else []


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class Branch:
    name: str
    local: bool = False
    remote: bool = False
    worktree: str = ""  # path to worktree, empty if none
    pr_status: str = "no-pr"
    pr_number: int | None = None
    commits_ahead: int = 0
    commits_behind: int = 0
    age: str = ""
    last_commit: str = ""
    safety: str = "needs-review"
    safety_detail: str = ""
    confidence: float = 0.5


# ---------------------------------------------------------------------------
# Data gathering
# ---------------------------------------------------------------------------

def get_branches() -> dict[str, Branch]:
    branches: dict[str, Branch] = {}

    # Detect default branch (main or master)
    default_branch = _run("git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null").split("/")[-1]
    if not default_branch:
        # Fallback: check if main or master exists
        for candidate in ("main", "master"):
            if _run(f"git rev-parse --verify {candidate} 2>/dev/null"):
                default_branch = candidate
                break
    if not default_branch:
        default_branch = "main"

    # Local unmerged branches
    for line in _run_lines(
        f"git branch --no-merged {default_branch} "
        "--format='%(refname:short)|%(committerdate:relative)|%(subject)'"
    ):
        parts = line.strip("'").split("|", 2)
        if len(parts) < 3:
            continue
        name, age, subject = parts
        branches[name] = Branch(name=name, local=True, age=age, last_commit=subject)

    # Remote unmerged branches
    for line in _run_lines(
        f"git branch -r --no-merged {default_branch} "
        "--format='%(refname:short)|%(committerdate:relative)|%(subject)'"
    ):
        parts = line.strip("'").split("|", 2)
        if len(parts) < 3:
            continue
        full_name, age, subject = parts
        if full_name in (f"origin/{default_branch}",) or full_name.startswith("origin/HEAD"):
            continue
        name = full_name.removeprefix("origin/")
        if name in branches:
            branches[name].remote = True
        else:
            branches[name] = Branch(name=name, remote=True, age=age, last_commit=subject)

    # Commit counts (ahead/behind)
    for name, info in branches.items():
        ref = name if info.local else f"origin/{name}"
        ahead = _run(f"git rev-list --count {default_branch}..{ref} 2>/dev/null")
        behind = _run(f"git rev-list --count {ref}..{default_branch} 2>/dev/null")
        info.commits_ahead = int(ahead) if ahead.isdigit() else 0
        info.commits_behind = int(behind) if behind.isdigit() else 0

    # Worktree detection — parse `git worktree list --porcelain`
    worktree_map = _get_worktree_map()
    for name, info in branches.items():
        if name in worktree_map:
            info.worktree = worktree_map[name]

    return branches


def _get_worktree_map() -> dict[str, str]:
    """Parse git worktree list --porcelain to map branch names to worktree paths."""
    output = _run("git worktree list --porcelain 2>/dev/null")
    if not output:
        return {}

    worktrees: dict[str, str] = {}
    current_path = ""
    for line in output.splitlines():
        if line.startswith("worktree "):
            current_path = line[len("worktree "):]
        elif line.startswith("branch refs/heads/"):
            branch_name = line[len("branch refs/heads/"):]
            if current_path:
                worktrees[branch_name] = current_path
    return worktrees


def ensure_gh_auth() -> bool:
    status = _run("gh auth status 2>&1")
    if "not logged in" in status.lower():
        return False

    test = _run("gh repo view --json nameWithOwner 2>&1")
    if "Could not resolve" in test:
        remote_url = _run("git remote get-url origin 2>/dev/null")
        for prefix in ("git@github.com-", "git@github.com:"):
            if prefix in remote_url:
                user = remote_url.split(prefix)[-1].split("/")[0]
                _run(f"gh auth switch --user {user} 2>/dev/null")
                break
    return True


def get_pr_status(branch_name: str) -> tuple[str, int | None]:
    for state in ("merged", "open", "closed"):
        result = _run(
            f"gh pr list --state {state} --head {branch_name} "
            "--json number --jq '.[0].number // empty' 2>/dev/null"
        )
        if result and result.isdigit():
            return state, int(result)
    return "no-pr", None


def get_merge_commit_sha(pr_number: int) -> str:
    """Get the squash merge commit SHA for a merged PR via gh CLI."""
    return _run(
        f"gh pr view {pr_number} --json mergeCommit --jq '.mergeCommit.oid' 2>/dev/null"
    )


def _parse_age_days(age: str) -> int | None:
    """Best-effort parse of a relative age string like '3 days ago' into days.

    Returns None if unparseable.  Handles: seconds, minutes, hours, days,
    weeks, months, years.
    """
    import re

    m = re.search(r"(\d+)\s+(second|minute|hour|day|week|month|year)s?\b", age)
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    multipliers = {
        "second": 0, "minute": 0, "hour": 0,
        "day": 1, "week": 7, "month": 30, "year": 365,
    }
    return n * multipliers.get(unit, 0)


def verify_branch_safety(
    branch_name: str,
    pr_number: int | None,
    pr_status: str,
    local: bool,
) -> tuple[str, str, float]:
    """Determine whether *branch_name* can be safely deleted.

    Returns ``(safety, safety_detail, confidence)`` where *safety* is one of:

    * ``"verified-safe"``  – content is fully present in main / PR was rejected
    * ``"likely-safe"``    – content appears superseded but not 100% certain
    * ``"has-unique-work"``– branch has work not yet in main
    * ``"needs-review"``   – couldn't determine automatically

    The function is intentionally conservative: when in doubt it returns
    ``"needs-review"`` so a human can make the call.
    """

    # --- Open PRs: active work ------------------------------------------------
    if pr_status == "open":
        return (
            "has-unique-work",
            f"PR #{pr_number} is still open — branch has active work.",
            0.9,
        )

    # --- Closed (not merged): intentionally rejected --------------------------
    if pr_status == "closed":
        return (
            "verified-safe",
            f"PR #{pr_number} was closed without merging — intentionally rejected.",
            0.95,
        )

    # --- Merged PRs: compare branch tip to squash commit ----------------------
    if pr_status == "merged" and pr_number is not None:
        merge_sha = get_merge_commit_sha(pr_number)
        if not merge_sha:
            return (
                "needs-review",
                f"PR #{pr_number} marked merged but could not retrieve merge commit SHA.",
                0.3,
            )

        ref = branch_name if local else f"origin/{branch_name}"

        # Fast path: diff branch tip against the merge commit itself
        diff_vs_merge = _run(
            f"git diff {merge_sha} {ref} --stat 2>/dev/null"
        )
        if not diff_vs_merge:
            return (
                "verified-safe",
                f"PR #{pr_number} squash-merged as {merge_sha[:10]}. "
                "Branch tip is identical to the merge commit.",
                1.0,
            )

        # Slower path: there IS a diff — check if every changed file matches
        # what's currently on the default branch (main advanced past the merge)
        changed_files = _run_lines(
            f"git diff {merge_sha} {ref} --name-only 2>/dev/null"
        )
        default_branch = (
            _run("git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null").split("/")[-1]
            or "main"
        )

        files_with_unique_work: list[str] = []
        for fpath in changed_files:
            # Compare the file on the branch to the same file on current main
            file_diff = _run(
                f"git diff {default_branch} {ref} -- {fpath} 2>/dev/null"
            )
            if file_diff:
                files_with_unique_work.append(fpath)

        if not files_with_unique_work:
            return (
                "verified-safe",
                f"PR #{pr_number} squash-merged. Branch differs from merge commit "
                f"but all {len(changed_files)} changed file(s) match current {default_branch}.",
                0.95,
            )

        if len(files_with_unique_work) <= 2 and len(changed_files) > 0:
            ratio = len(files_with_unique_work) / len(changed_files)
            if ratio <= 0.25:
                return (
                    "likely-safe",
                    f"PR #{pr_number} squash-merged. {len(files_with_unique_work)}/{len(changed_files)} "
                    f"file(s) differ from {default_branch} (likely superseded): "
                    f"{', '.join(files_with_unique_work)}.",
                    0.75,
                )

        return (
            "has-unique-work",
            f"PR #{pr_number} squash-merged but {len(files_with_unique_work)} file(s) "
            f"differ from current {default_branch}: {', '.join(files_with_unique_work[:5])}.",
            0.7,
        )

    # --- No PR: use age heuristics -------------------------------------------
    if pr_status == "no-pr":
        ref = branch_name if local else f"origin/{branch_name}"
        age_str = _run(
            f"git log -1 --format='%cr' {ref} 2>/dev/null"
        )
        return (
            "needs-review",
            f"No associated PR. Last activity: {age_str or 'unknown'}. "
            "Manual review recommended.",
            0.3,
        )

    # Fallback
    return ("needs-review", "Could not determine safety automatically.", 0.3)


# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------

def build_prompt(branches: list[Branch]) -> str:
    repo_name = _run("basename $(git rev-parse --show-toplevel) 2>/dev/null") or "this repo"
    default_branch = _run("git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null").split("/")[-1] or "main"
    main_sha = _run(f"git rev-parse --short {default_branch} 2>/dev/null") or "unknown"
    main_date = _run(f"git log -1 --format='%cr' {default_branch} 2>/dev/null") or "unknown"

    # Branch summaries
    rows: list[str] = []
    for b in sorted(branches, key=lambda x: x.name):
        loc = []
        if b.local:
            loc.append("local")
        if b.remote:
            loc.append("remote")

        pr_info = "no PR"
        if b.pr_status == "merged":
            pr_info = f"PR #{b.pr_number} merged"
        elif b.pr_status == "open":
            pr_info = f"PR #{b.pr_number} open"
        elif b.pr_status == "closed":
            pr_info = f"PR #{b.pr_number} closed (not merged)"

        worktree_line = ""
        if b.worktree:
            worktree_line = f"\n    Worktree: {b.worktree}"

        safety_line = ""
        if b.safety != "needs-review" or b.safety_detail:
            safety_line = (
                f"\n    Safety: **{b.safety}** (confidence: {b.confidence:.0%})"
                f"\n    Detail: {b.safety_detail}"
            )

        rows.append(
            f"  - **{b.name}** ({'+'.join(loc)})\n"
            f"    PR: {pr_info}\n"
            f"    Commits: {b.commits_ahead} ahead, {b.commits_behind} behind {default_branch}\n"
            f"    Age: {b.age}\n"
            f"    Last commit: {b.last_commit}"
            f"{worktree_line}"
            f"{safety_line}"
        )

    # Per-branch detail: diff stats, commit list, new files
    details: list[str] = []
    for b in sorted(branches, key=lambda x: x.name):
        ref = b.name if b.local else f"origin/{b.name}"
        commits = _run(f"git log {default_branch}..{ref} --oneline 2>/dev/null | head -10")
        diff_stat = _run(f"git diff {default_branch} {ref} --stat 2>/dev/null | tail -5")
        new_files = _run(f"git diff {default_branch} {ref} --diff-filter=A --name-only 2>/dev/null | head -10")

        section = f"### {b.name}\n"
        if commits:
            section += f"Commits (up to 10):\n```\n{commits}\n```\n"
        if diff_stat:
            section += f"Diff stat vs {default_branch}:\n```\n{diff_stat}\n```\n"
        if new_files:
            section += f"New files only on branch:\n```\n{new_files}\n```\n"
        elif diff_stat:
            section += f"No new files (all changes are to existing files).\n"
        else:
            section += f"No diff vs {default_branch}.\n"
        details.append(section)

    # Build per-branch pre-computed safety data for the schema example
    precomputed: list[dict[str, object]] = []
    for b in sorted(branches, key=lambda x: x.name):
        precomputed.append({
            "name": b.name,
            "prStatus": b.pr_status,
            "prNumber": b.pr_number,
            "local": b.local,
            "remote": b.remote,
            "worktree": b.worktree or None,
            "commits": b.commits_ahead,
            "behind": b.commits_behind,
            "age": b.age,
            "lastCommit": b.last_commit,
            "safety": b.safety,
            "safetyDetail": b.safety_detail,
            "confidence": b.confidence,
            "action": "FILL-IN",
            "recommendation": "FILL-IN",
        })

    schema_example = json.dumps({
        "repo": "repo-name",
        "branches": [{
            "name": "branch-name",
            "prStatus": "merged",
            "prNumber": 42,
            "local": True,
            "remote": False,
            "worktree": None,
            "commits": 5,
            "behind": 12,
            "age": "3 days ago",
            "lastCommit": "feat: add example feature",
            "safety": "verified-safe",
            "safetyDetail": "PR #42 squash-merged. No post-merge commits. Content identical to main.",
            "confidence": 0.95,
            "action": "delete",
            "recommendation": "Safe to delete. PR #42 merged. All content verified in main.",
        }],
    }, indent=2)

    precomputed_json = json.dumps({
        "repo": repo_name,
        "branches": precomputed,
    }, indent=2)

    branches_block = "\n\n".join(rows)
    details_block = "\n".join(details)

    return f"""I need help triaging the unmerged git branches in my repo. I've gathered
the data below — please analyze each branch and respond with **JSON only**.

I have an HTML dashboard template that will render this JSON into an interactive
triage page. Just give me the JSON and I'll paste it in.

## Context

- **Repo:** {repo_name}
- **Default branch tip:** {main_sha} ({main_date})
- **Total unmerged branches:** {len(branches)}
- **This repo likely uses squash merges** — commit hashes on branches may NOT
  appear in the default branch's history. Use content-based analysis (diff stats,
  commit messages, file presence) instead of hash-based ancestry checks.

## Branch Summary

{branches_block}

## Detailed Branch Data

{details_block}

## Pre-computed Safety Verification

The following JSON contains pre-computed safety verdicts from automated
squash-commit verification. The `safety`, `safetyDetail`, and `confidence`
fields have already been filled in — use these as-is (do NOT override them).
You only need to fill in `action` and `recommendation` for each branch.

```json
{precomputed_json}
```

## Output: JSON conforming to this schema

Respond with **only** a JSON object (in a ```json code fence). No other text.

Every field is required for every branch. Here's the schema with one example entry:

```json
{schema_example}
```

### Field definitions

| Field | Type | Values |
|-------|------|--------|
| `name` | string | Exact branch name from the data above |
| `prStatus` | string | `"merged"` \\| `"closed"` \\| `"open"` \\| `"no-pr"` |
| `prNumber` | int or null | PR number, or `null` if no PR |
| `local` | boolean | Whether the branch exists locally |
| `remote` | boolean | Whether the branch exists on origin |
| `worktree` | string or null | Path to active git worktree, or `null` |
| `commits` | int or null | Commits ahead of default branch |
| `behind` | int or null | Commits behind default branch |
| `age` | string | Human-readable age (e.g. `"3 weeks ago"`) |
| `lastCommit` | string | Last commit message subject line |
| `safety` | string | Pre-computed: use the value from the pre-computed JSON above |
| `safetyDetail` | string | Pre-computed: use the value from the pre-computed JSON above |
| `confidence` | float | Pre-computed: use the value from the pre-computed JSON above |
| `action` | string | `"delete"` \\| `"keep"` \\| `"next-up"` \\| `"park"` \\| `"rebase-pr"` \\| `"cherry-pick"` |
| `recommendation` | string | 1 sentence actionable recommendation |

### Decision guidelines

- **Active worktree** → always `"keep"` (deleting would break the worktree)
- **PR merged + no unique work** → `"verified-safe"` / `"delete"`
- **PR merged + minor diff from main advancing** → `"likely-safe"` / `"delete"`
- **PR closed (not merged)** → usually `"delete"` (intentionally rejected)
- **PR open** → `"keep"`
- **No PR, < 7 days old** → `"keep"` (likely active)
- **No PR, 7-30 days old** → `"next-up"` or `"rebase-pr"`
- **No PR, > 30 days old** → `"park"` (stale)
- **Release automation** (release-please, renovate) → `"keep"`
- Branches with unique work not in main → `"has-unique-work"`, action depends on value
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _branches_to_json(branches: list[Branch], repo_name: str) -> dict[str, object]:
    """Convert Branch list to the JSON schema expected by generate_html.py."""
    return {
        "repo": repo_name,
        "branches": [
            {
                "name": b.name,
                "prStatus": b.pr_status,
                "prNumber": b.pr_number,
                "local": b.local,
                "remote": b.remote,
                "worktree": b.worktree or None,
                "commits": b.commits_ahead,
                "behind": b.commits_behind,
                "age": b.age,
                "lastCommit": b.last_commit,
                "safety": b.safety,
                "safetyDetail": b.safety_detail,
                "confidence": b.confidence,
                # action and recommendation are filled in by the AI or caller
                "action": "FILL-IN",
                "recommendation": "FILL-IN",
            }
            for b in sorted(branches, key=lambda x: x.name)
        ],
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Gather branch data and generate AI triage prompt")
    parser.add_argument("--copy", action="store_true", help="Also copy prompt to clipboard (macOS pbcopy)")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON data instead of AI prompt (for generate_html.py pipeline)")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Write output to file instead of stdout")
    parser.add_argument("--parallel", type=int, default=4, help="Max parallel workers (default: 4)")
    args = parser.parse_args()

    # Verify we're in a git repo
    if not _run("git rev-parse --is-inside-work-tree 2>/dev/null"):
        print("Error: not inside a git repository.", file=sys.stderr)
        sys.exit(1)

    print("Gathering branch data...", file=sys.stderr)
    branches = get_branches()
    if not branches:
        print("No unmerged branches found.", file=sys.stderr)
        sys.exit(0)

    # Get PR status in parallel
    gh_ok = ensure_gh_auth()
    if gh_ok:
        print(f"Checking PR status for {len(branches)} branches...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futures = {pool.submit(get_pr_status, name): name for name in branches}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    status, number = future.result()
                    branches[name].pr_status = status
                    branches[name].pr_number = number
                except Exception:
                    pass

        # Run safety verification in parallel (depends on PR status being set)
        print(f"Verifying branch safety for {len(branches)} branches...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            safety_futures = {
                pool.submit(
                    verify_branch_safety,
                    name,
                    branches[name].pr_number,
                    branches[name].pr_status,
                    branches[name].local,
                ): name
                for name in branches
            }
            for future in as_completed(safety_futures):
                name = safety_futures[future]
                try:
                    safety, detail, confidence = future.result()
                    branches[name].safety = safety
                    branches[name].safety_detail = detail
                    branches[name].confidence = confidence
                except Exception:
                    pass  # defaults to "needs-review"
    else:
        print("Warning: gh CLI not authenticated, skipping PR status and safety checks.", file=sys.stderr)

    repo_name = _run("basename $(git rev-parse --show-toplevel) 2>/dev/null") or "repo"
    branch_list = list(branches.values())

    # Choose output format
    if args.json:
        output = json.dumps(_branches_to_json(branch_list, repo_name), indent=2)
        print(f"Generated JSON for {len(branch_list)} branches.", file=sys.stderr)
    else:
        print("Generating prompt...", file=sys.stderr)
        output = build_prompt(branch_list)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"✅ Wrote output to {args.output}", file=sys.stderr)
    else:
        print(output)

    if args.copy and not args.output:
        try:
            proc = subprocess.run(["pbcopy"], input=output, text=True, capture_output=True, timeout=5)
            if proc.returncode == 0:
                print("\n--- ✂️  Copied to clipboard! ---", file=sys.stderr)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("(Clipboard copy not available — output printed to stdout)", file=sys.stderr)


if __name__ == "__main__":
    main()
