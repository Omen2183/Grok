#!/usr/bin/env python3
"""CLI backend for dnd-skills-manager — suite maintenance, validation, and drift checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

UTILS_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"
sys.path.insert(0, str(UTILS_SCRIPTS))

from paths import get_skills_root, get_workspace_root  # noqa: E402

SKILLS_DIR = get_skills_root()
WORKSPACE_ROOT = get_workspace_root()
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"

KEY_FILES = ("SKILL.md",)


def run_cmd(cmd: list[str], cwd: Path | None = None, timeout: int = 180) -> dict[str, Any]:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
    except Exception as exc:
        return {"returncode": 1, "stdout": "", "stderr": str(exc), "success": False}


def get_all_skills(*, dnd_only: bool = False) -> list[Path]:
    skills: list[Path] = []
    for item in sorted(SKILLS_DIR.iterdir()):
        if not item.is_dir() or item.name.startswith(("_", ".")):
            continue
        if dnd_only and not item.name.startswith("dnd-"):
            continue
        if (item / "SKILL.md").exists():
            skills.append(item)
    return skills


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cmd_status(_args: argparse.Namespace) -> int:
    print("=== D&D Skills Manager — Status ===\n")
    print(f"Skills root:   {SKILLS_DIR}")
    print(f"Workspace:     {WORKSPACE_ROOT}")
    print(f"Scripts dir:   {SCRIPTS_DIR} ({'found' if SCRIPTS_DIR.is_dir() else 'missing'})\n")

    if (WORKSPACE_ROOT / ".git").exists():
        res = run_cmd(["git", "status", "--short"])
        print("Local git status:")
        print(res["stdout"].strip() or "  Working tree is clean")
        res = run_cmd(["git", "log", "--oneline", "-6"])
        print("\nRecent commits:")
        print(res["stdout"].strip() or "  (none)")
    else:
        print("Not a git repo — status limited to skills inventory.")

    skills = get_all_skills()
    print(f"\nSkills installed: {len(skills)}")
    print("  " + ", ".join(s.name for s in skills))
    return 0


def cmd_inventory(_args: argparse.Namespace) -> int:
    print("=== Skills Inventory ===\n")
    for skill in get_all_skills():
        has_scripts = (skill / "scripts").is_dir() and any((skill / "scripts").glob("*.py"))
        has_tests = (skill / "tests").is_dir() and any((skill / "tests").glob("*.py"))
        tags: list[str] = []
        if has_scripts:
            tags.append("scripts")
        if has_tests:
            tags.append("tests")
        label = " | ".join(tags) if tags else "docs-only"
        print(f"  {skill.name:32} {label}")
    print(f"\nTotal: {len(get_all_skills())}")
    return 0


def _run_script(name: str, results: dict[str, Any]) -> None:
    script = SCRIPTS_DIR / name
    if not script.exists():
        print(f"  skip {name} (not found — run from full repo clone)")
        return
    print(f"  -> {name}")
    res = run_cmd([sys.executable, str(script)])
    results[name] = res
    if res["stdout"].strip():
        print(res["stdout"].strip())
    if res["stderr"].strip():
        print(res["stderr"].strip(), file=sys.stderr)


def cmd_validate(_args: argparse.Namespace) -> int:
    print("=== Running Validation Suite ===\n")
    results: dict[str, Any] = {}
    for script in (
        "validate_runtime.py",
        "validate_skills.py",
        "validate_skill_docs.py",
        "validate_orchestration.py",
        "validate_backends.py",
    ):
        _run_script(script, results)

    failed = [name for name, res in results.items() if not res.get("success")]
    if failed:
        print(f"\nFailed: {', '.join(failed)}")
        return 1
    if not results:
        print("\nNo repo scripts found. Copy the GitHub repo or set GROK_WORKSPACE_ROOT.")
        return 1
    print("\nAll validations passed.")
    return 0


def cmd_score(_args: argparse.Namespace) -> int:
    score_script = SCRIPTS_DIR / "suite_score.py"
    if not score_script.exists():
        print("suite_score.py not found — run from full repo clone.")
        return 1
    print("=== Suite Score (10-point) ===\n")
    res = run_cmd([sys.executable, str(score_script)], timeout=300)
    if res["stdout"]:
        print(res["stdout"])
    if res["stderr"]:
        print(res["stderr"], file=sys.stderr)
    return res["returncode"]


def cmd_smoke(_args: argparse.Namespace) -> int:
    smoke = SCRIPTS_DIR / "smoke_test.py"
    if not smoke.exists():
        print("smoke_test.py not found — run from full repo clone.")
        return 1
    print("=== Smoke Test ===\n")
    res = run_cmd([sys.executable, str(smoke)], timeout=240)
    if res["stdout"]:
        print(res["stdout"])
    if res["stderr"]:
        print(res["stderr"], file=sys.stderr)
    return res["returncode"]


def cmd_git(args: argparse.Namespace) -> int:
    res = run_cmd(["git", *args.git_args])
    if res["stdout"]:
        print(res["stdout"])
    if res["stderr"]:
        print(res["stderr"], file=sys.stderr)
    return res["returncode"]


def cmd_pull(args: argparse.Namespace) -> int:
    print("=== GitHub Pull / Sync ===\n")
    if args.dry_run:
        print("[dry-run] Use chat with connected GitHub tools to compare trees.\n")
    print("Say: \"pull latest from github\" or \"skills manager drift\"")
    print("Canonical repo: https://github.com/Omen2183/Grok (main)")
    return 0


def cmd_drift(_args: argparse.Namespace) -> int:
    print("=== Drift Detection ===\n")
    print("Local check:  skills_manager.py sync-check --against <other-skills-root>")
    print("Remote check: ask in chat to compare with GitHub main")
    return 0


def _compare_roots(local: Path, other: Path, *, dnd_only: bool = True) -> dict[str, Any]:
    report: dict[str, Any] = {"local": str(local), "other": str(other), "skills": []}
    names = {p.name for p in get_all_skills(dnd_only=dnd_only)}
    if other.is_dir():
        for item in other.iterdir():
            if item.is_dir() and item.name.startswith("dnd-"):
                names.add(item.name)

    for name in sorted(names):
        entry: dict[str, Any] = {"skill": name, "status": "ok", "files": []}
        local_skill = local / name
        other_skill = other / name
        if not local_skill.is_dir():
            entry["status"] = "missing_local"
            report["skills"].append(entry)
            continue
        if not other_skill.is_dir():
            entry["status"] = "missing_other"
            report["skills"].append(entry)
            continue

        checked: list[str] = []
        for rel in KEY_FILES:
            lf, of = local_skill / rel, other_skill / rel
            if lf.exists() and of.exists():
                checked.append(rel)
                if file_sha256(lf) != file_sha256(of):
                    entry["files"].append({"path": rel, "match": False})
            elif lf.exists() != of.exists():
                entry["files"].append({"path": rel, "match": False, "note": "presence mismatch"})

        for script_dir in ("scripts",):
            lp, op = local_skill / script_dir, other_skill / script_dir
            if lp.is_dir() and op.is_dir():
                for lf in sorted(lp.glob("*.py")):
                    of = op / lf.name
                    if not of.exists():
                        entry["files"].append({"path": f"{script_dir}/{lf.name}", "match": False, "note": "missing"})
                    elif file_sha256(lf) != file_sha256(of):
                        entry["files"].append({"path": f"{script_dir}/{lf.name}", "match": False})

        if entry["files"]:
            entry["status"] = "drift"
        report["skills"].append(entry)

    report["drift_count"] = sum(1 for s in report["skills"] if s["status"] == "drift")
    report["aligned"] = report["drift_count"] == 0 and all(
        s["status"] in ("ok",) for s in report["skills"]
    )
    return report


def cmd_sync_all(_args: argparse.Namespace) -> int:
    """Run registry check, full validate, smoke, and pytest."""
    steps = [
        ("registry_sync", [sys.executable, str(SCRIPTS_DIR / "registry_sync.py"), "--check"]),
        ("validate", None),
        ("score", None),
        ("smoke", None),
        ("pytest", [sys.executable, "-m", "pytest", str(WORKSPACE_ROOT / ".grok" / "skills"), "-q", "--tb=no"]),
    ]
    failed: list[str] = []
    for name, cmd in steps:
        if name == "validate":
            code = cmd_validate(argparse.Namespace())
        elif name == "score":
            code = cmd_score(argparse.Namespace())
        elif name == "smoke":
            code = cmd_smoke(argparse.Namespace())
        elif cmd:
            res = run_cmd(cmd)
            code = 0 if res["success"] else 1
            if not res["success"] and res["stderr"]:
                print(res["stderr"], file=sys.stderr)
        else:
            code = 1
        if code != 0:
            failed.append(name)
    if failed:
        print(f"sync-all failed: {', '.join(failed)}")
        return 1
    print("sync-all passed.")
    return 0


def cmd_sync_check(args: argparse.Namespace) -> int:
    other = Path(args.against).expanduser().resolve()
    if not other.is_dir():
        print(f"Not found: {other}")
        return 1
    report = _compare_roots(SKILLS_DIR, other, dnd_only=not args.all_skills)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Local:  {SKILLS_DIR}")
        print(f"Other:  {other}\n")
        for skill in report["skills"]:
            if skill["status"] == "ok":
                print(f"  OK   {skill['skill']}")
            else:
                print(f"  {skill['status'].upper():6} {skill['skill']}")
                for f in skill.get("files", []):
                    print(f"         - {f['path']}")
        print(f"\nDrift: {report['drift_count']} skill(s)")
    return 0 if report.get("aligned") else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="dnd-skills-manager — maintain the Grok D&D suite")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("inventory").set_defaults(func=cmd_inventory)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
    sub.add_parser("score", help="10-point production grade with evidence").set_defaults(func=cmd_score)
    sub.add_parser("smoke").set_defaults(func=cmd_smoke)

    git_p = sub.add_parser("git")
    git_p.add_argument("git_args", nargs=argparse.REMAINDER)
    git_p.set_defaults(func=cmd_git)

    pull_p = sub.add_parser("pull")
    pull_p.add_argument("--dry-run", action="store_true")
    pull_p.set_defaults(func=cmd_pull)

    sub.add_parser("drift").set_defaults(func=cmd_drift)
    sub.add_parser("sync-all", help="registry_sync + validate + smoke + pytest").set_defaults(func=cmd_sync_all)

    sync_p = sub.add_parser("sync-check", help="Compare local skills to another skills root")
    sync_p.add_argument("--against", required=True, help="Path to other .grok/skills or export skills/ folder")
    sync_p.add_argument("--all-skills", action="store_true", help="Include non-dnd skills")
    sync_p.add_argument("--json", action="store_true")
    sync_p.set_defaults(func=cmd_sync_check)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())