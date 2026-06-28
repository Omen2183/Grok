#!/usr/bin/env python3
"""Aggregate D&D skills suite quality into a 10-point score with evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".grok" / "skills"
SCRIPTS = REPO / "scripts"


def _run(script: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    try:
        data = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
    except json.JSONDecodeError:
        data = {}
    return {"returncode": proc.returncode, "data": data}


def _pytest() -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(SKILLS), "-q", "--tb=no"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    passed = failed = 0
    for line in proc.stdout.splitlines():
        if " passed" in line:
            parts = line.strip().split()
            if parts and parts[0].isdigit():
                passed = int(parts[0])
        if " failed" in line:
            parts = line.strip().split()
            for i, p in enumerate(parts):
                if p == "failed" and i > 0 and parts[i - 1].isdigit():
                    failed = int(parts[i - 1])
    return {
        "returncode": proc.returncode,
        "passed": passed,
        "failed": failed,
        "ok": proc.returncode == 0 and failed == 0,
    }


def _smoke() -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "smoke_test.py")],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=240,
    )
    return {"returncode": proc.returncode, "ok": proc.returncode == 0}


def _skill_test_coverage() -> dict:
    dnd_skills = sorted(p for p in SKILLS.iterdir() if p.is_dir() and p.name.startswith("dnd-"))
    with_tests = [s.name for s in dnd_skills if (s / "tests").is_dir() and any((s / "tests").glob("test_*.py"))]
    missing = [s.name for s in dnd_skills if s.name not in with_tests]
    return {
        "total": len(dnd_skills),
        "with_tests": len(with_tests),
        "missing": missing,
        "ok": len(missing) == 0,
    }


def score() -> dict:
    dimensions: list[dict] = []
    total = 0.0
    max_score = 10.0

    checks = [
        ("Runtime & paths", 1.0, "validate_runtime.py", lambda d: d.get("valid")),
        ("Skill structure", 1.0, "validate_skills.py", lambda d: d.get("failed", 1) == 0),
        ("Documentation", 2.0, "validate_skill_docs.py", lambda d: d.get("valid")),
        ("Orchestration", 1.0, "validate_orchestration.py", lambda d: d.get("valid")),
        ("Backend depth", 2.0, "validate_backends.py", lambda d: d.get("valid")),
    ]

    for label, weight, script, pred in checks:
        res = _run(script)
        ok = res["returncode"] == 0 and pred(res["data"])
        earned = weight if ok else 0.0
        total += earned
        dimensions.append(
            {
                "dimension": label,
                "weight": weight,
                "score": earned,
                "pass": ok,
                "evidence": res["data"],
            }
        )

    coverage = _skill_test_coverage()
    test_ok = coverage["ok"]
    pytest = _pytest()
    test_score = 2.0 if test_ok and pytest["ok"] else (1.0 if test_ok or pytest["ok"] else 0.0)
    total += test_score
    dimensions.append(
        {
            "dimension": "Test coverage",
            "weight": 2.0,
            "score": test_score,
            "pass": test_ok and pytest["ok"],
            "evidence": {**coverage, "pytest": pytest},
        }
    )

    smoke = _smoke()
    smoke_score = 1.0 if smoke["ok"] else 0.0
    total += smoke_score
    dimensions.append(
        {
            "dimension": "End-to-end smoke",
            "weight": 1.0,
            "score": smoke_score,
            "pass": smoke["ok"],
            "evidence": smoke,
        }
    )

    rating = round(total, 1)
    grade = (
        "10/10 — table-grade production"
        if rating >= 10.0
        else f"{rating}/10 — gaps remain"
    )

    return {
        "suite_version": "5.3.0",
        "skills_count": coverage["total"],
        "score": rating,
        "max_score": max_score,
        "grade": grade,
        "production_ready": rating >= 10.0,
        "dimensions": dimensions,
    }


def main() -> int:
    report = score()
    print(json.dumps(report, indent=2))
    return 0 if report["production_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())