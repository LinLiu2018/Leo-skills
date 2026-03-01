#!/usr/bin/env python3
"""Sync skill default schedules into OpenClaw cron jobs."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import importlib
import inspect
import json
from pathlib import Path
import shutil
import sys
import uuid
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
SKILLS_ROOT = SRC_ROOT / "leo_skills"
OPENCLAW_JOBS = Path.home() / ".openclaw" / "cron" / "jobs.json"
DEFAULT_TARGET_SKILLS = {
    "video_monitor_skill",
    "competitor_scraper_skill",
    "auto_logger_skill",
    "twitter_monitor_skill",
    "evolution_skill",
}

for path in (ROOT, SRC_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

def _json_out(payload: Dict[str, Any], exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return exit_code


def _module_name_from_file(path: Path) -> Optional[str]:
    try:
        relative = path.relative_to(ROOT).with_suffix("")
    except ValueError:
        return None
    return ".".join(relative.parts)


def _candidate_skill_files(skill_name: str, skill_path: Optional[str]) -> List[Path]:
    candidates: List[Path] = []
    if skill_path:
        path = Path(skill_path)
        for item in (ROOT / path, SRC_ROOT / path):
            if item.is_file() and item.name == f"{skill_name}.py":
                candidates.append(item.resolve())
            elif item.is_dir():
                py_file = item / f"{skill_name}.py"
                if py_file.exists():
                    candidates.append(py_file.resolve())

    for found in SKILLS_ROOT.glob(f"**/{skill_name}.py"):
        if "scripts" in found.parts:
            continue
        candidates.append(found.resolve())

    unique: List[Path] = []
    seen = set()
    for item in candidates:
        key = str(item)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _iter_skill_classes(module: Any, preferred_name: str) -> Iterable[type]:
    preferred = getattr(module, preferred_name, None)
    if inspect.isclass(preferred):
        yield preferred
    for _, member in inspect.getmembers(module, inspect.isclass):
        if member is preferred:
            continue
        if member.__module__ != module.__name__:
            continue
        if hasattr(member, "execute") and callable(getattr(member, "execute")):
            yield member


def _load_skill_class(skill_name: str, skill_path: Optional[str]) -> Optional[type]:
    class_name = "".join(part.capitalize() for part in skill_name.split("_"))
    if not class_name.endswith("Skill"):
        class_name += "Skill"

    for skill_file in _candidate_skill_files(skill_name, skill_path):
        module_name = _module_name_from_file(skill_file)
        if not module_name:
            continue
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        for cls in _iter_skill_classes(module, class_name):
            return cls
    return None


def _load_jobs() -> Dict[str, Any]:
    if OPENCLAW_JOBS.exists():
        with OPENCLAW_JOBS.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, dict) and isinstance(data.get("jobs"), list):
                return data
    return {"version": 1, "jobs": []}


def _backup_jobs() -> Optional[Path]:
    if not OPENCLAW_JOBS.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = OPENCLAW_JOBS.with_name(f"jobs.backup.{stamp}.json")
    shutil.copy2(OPENCLAW_JOBS, backup)
    return backup


def _default_delivery(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    for job in jobs:
        delivery = job.get("delivery")
        if isinstance(delivery, dict) and delivery.get("channel"):
            return copy.deepcopy(delivery)
    return {
        "mode": "announce",
        "channel": "feishu",
        "to": "ou_099438b3924bd34e5f9445bc8220a460",
    }


def _build_job(skill_name: str, schedule: str, delivery: Dict[str, Any]) -> Dict[str, Any]:
    now_ms = int(datetime.now().timestamp() * 1000)
    return {
        "id": str(uuid.uuid4()),
        "agentId": "leo-assistant",
        "name": f"skill_{skill_name}",
        "description": f"Direct execution for {skill_name}",
        "enabled": True,
        "createdAtMs": now_ms,
        "updatedAtMs": now_ms,
        "schedule": {
            "kind": "cron",
            "expr": schedule,
            "tz": "Asia/Shanghai",
            "staggerMs": 30000,
        },
        "sessionTarget": "main",
        "wakeMode": "now",
        "payload": {
            "kind": "systemEvent",
            "text": f"skill:{skill_name}:execute",
        },
        "delivery": delivery,
    }


def sync_schedules(
    dry_run: bool = False,
    target_skills: Optional[set[str]] = None,
) -> Dict[str, Any]:
    jobs_config = _load_jobs()
    jobs = jobs_config.setdefault("jobs", [])
    delivery_template = _default_delivery(jobs)
    existing_by_name = {str(job.get("name", "")): job for job in jobs}

    updated: List[str] = []
    added: List[str] = []
    skipped: List[str] = []

    skill_candidates: Dict[str, Optional[str]] = {}
    for py_file in SKILLS_ROOT.glob("**/*_skill.py"):
        if any(part in {"scripts", "output", "test_output", "__pycache__", "content-benchmark"} for part in py_file.parts):
            continue
        if target_skills is not None and py_file.stem not in target_skills:
            continue
        skill_candidates.setdefault(py_file.stem, str(py_file.parent))

    if target_skills is not None:
        for skill_name in target_skills:
            skill_candidates.setdefault(skill_name, None)

    for skill_name, skill_path in sorted(skill_candidates.items()):
        if target_skills is not None and skill_name not in target_skills:
            continue
        cls = _load_skill_class(skill_name, skill_path)
        if cls is None:
            skipped.append(f"{skill_name}:class_not_found")
            continue

        supports_direct = bool(
            getattr(cls, "supports_direct_execution", False)
            or getattr(getattr(cls, "__dict__", {}), "supports_direct_execution", False)
        )
        schedule = getattr(cls, "default_schedule", None)
        if not supports_direct or not schedule:
            continue

        job_name = f"skill_{skill_name}"
        if job_name in existing_by_name:
            job = existing_by_name[job_name]
            job.setdefault("schedule", {})
            job["enabled"] = True
            job["schedule"]["kind"] = "cron"
            job["schedule"]["expr"] = schedule
            job["schedule"]["tz"] = job["schedule"].get("tz", "Asia/Shanghai")
            job["schedule"]["staggerMs"] = job["schedule"].get("staggerMs", 30000)
            job["payload"] = {"kind": "systemEvent", "text": f"skill:{skill_name}:execute"}
            job["sessionTarget"] = job.get("sessionTarget", "main")
            job["wakeMode"] = job.get("wakeMode", "now")
            job["updatedAtMs"] = int(datetime.now().timestamp() * 1000)
            updated.append(skill_name)
        else:
            jobs.append(_build_job(skill_name, schedule, copy.deepcopy(delivery_template)))
            added.append(skill_name)

    backup_path = None if dry_run else _backup_jobs()
    if not dry_run:
        OPENCLAW_JOBS.parent.mkdir(parents=True, exist_ok=True)
        with OPENCLAW_JOBS.open("w", encoding="utf-8") as handle:
            json.dump(jobs_config, handle, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "status": "success",
        "dry_run": dry_run,
        "target_skills": sorted(target_skills) if target_skills else "all",
        "backup": str(backup_path) if backup_path else None,
        "added_count": len(added),
        "updated_count": len(updated),
        "added": added,
        "updated": updated,
        "skipped_count": len(skipped),
        "skipped": skipped,
        "jobs_path": str(OPENCLAW_JOBS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync default skill schedules into OpenClaw jobs.")
    parser.add_argument("--dry-run", action="store_true", help="Show summary without writing jobs.json")
    parser.add_argument("--all", action="store_true", help="Sync all direct-executable skills with default_schedule")
    parser.add_argument(
        "--skills",
        default="",
        help="Comma-separated skill names to sync, e.g. video_monitor_skill,auto_logger_skill",
    )
    args = parser.parse_args()

    try:
        if args.skills.strip():
            target_skills = {item.strip() for item in args.skills.split(",") if item.strip()}
        elif args.all:
            target_skills = None
        else:
            target_skills = set(DEFAULT_TARGET_SKILLS)
        result = sync_schedules(dry_run=args.dry_run, target_skills=target_skills)
        return _json_out(result, exit_code=0)
    except Exception as exc:
        return _json_out(
            {"success": False, "status": "error", "error": str(exc), "jobs_path": str(OPENCLAW_JOBS)},
            exit_code=1,
        )


if __name__ == "__main__":
    raise SystemExit(main())
