#!/usr/bin/env python3
"""Direct skill execution entrypoint for OpenClaw system events."""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
SKILLS_ROOT = SRC_ROOT / "leo_skills"

for path in (ROOT, SRC_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from leo_skills.core.base_executor import ExecutionContext  # noqa: E402


def _json_out(payload: Dict[str, Any], exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return exit_code


def _parse_payload(raw: str) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {"value": data}
    except Exception as exc:
        parse_error = str(exc)

    # PowerShell 常见输入会被转成 {city:ningbo} 这种非 JSON 结构，这里做兼容。
    text = str(raw).strip()
    if text.startswith("{") and text.endswith("}") and ":" in text:
        inner = text[1:-1].strip()
        parsed: Dict[str, Any] = {}
        for pair in re.split(r"\s*,\s*", inner):
            if not pair:
                continue
            if ":" not in pair:
                continue
            key, value = pair.split(":", 1)
            key = key.strip().strip("'\"")
            value = value.strip().strip("'\"")
            if key:
                parsed[key] = value
        if parsed:
            return parsed

    return {"_payload_parse_error": parse_error}


def _camel_case_skill_name(skill_name: str) -> str:
    class_name = "".join(part.capitalize() for part in skill_name.split("_"))
    if not class_name.endswith("Skill"):
        class_name += "Skill"
    return class_name


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
        raw_candidates = [ROOT / path, SRC_ROOT / path]
        for item in raw_candidates:
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

    seen = set()
    unique: List[Path] = []
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


def _load_skill_class(skill_name: str, skill_path: Optional[str]) -> Tuple[Optional[type], Optional[str]]:
    class_name = _camel_case_skill_name(skill_name)
    errors: List[str] = []

    for skill_file in _candidate_skill_files(skill_name, skill_path):
        module_name = _module_name_from_file(skill_file)
        if not module_name:
            continue
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            errors.append(f"{module_name}: {exc}")
            continue

        for cls in _iter_skill_classes(module, class_name):
            return cls, None

    return None, "; ".join(errors) if errors else "no candidate module found"


def _normalize_result(result: Any) -> Dict[str, Any]:
    if hasattr(result, "to_dict") and callable(result.to_dict):
        result = result.to_dict()

    if isinstance(result, dict):
        payload = dict(result)
    else:
        payload = {"data": result}

    if "metadata" in payload and isinstance(payload["metadata"], dict):
        metadata = payload["metadata"]
        if "content" in metadata and "content" not in payload:
            payload["content"] = metadata["content"]
        if "markdown" in metadata and "markdown" not in payload:
            payload["markdown"] = metadata["markdown"]

    if "content" not in payload:
        if isinstance(payload.get("data"), dict):
            payload["content"] = payload["data"].get("summary") or payload["data"].get("message", "")
        else:
            payload["content"] = payload.get("message", "")

    if "markdown" not in payload:
        payload["markdown"] = payload.get("content", "")

    if "success" not in payload:
        status = str(payload.get("status", "success")).lower()
        payload["success"] = status not in {"error", "failed", "fail"}
    if "status" not in payload:
        payload["status"] = "success" if payload["success"] else "error"
    return payload


def _execute_skill(skill_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    setup_stdout = io.StringIO()
    setup_stderr = io.StringIO()
    with contextlib.redirect_stdout(setup_stdout), contextlib.redirect_stderr(setup_stderr):
        skill_cls, import_error = _load_skill_class(skill_name, skill_path=None)
        if skill_cls is None:
            return {
                "success": False,
                "status": "error",
                "skill": skill_name,
                "error": f"Skill class not found: {skill_name}",
                "details": import_error,
            }

        try:
            skill = skill_cls()
        except Exception as exc:
            return {
                "success": False,
                "status": "error",
                "skill": skill_name,
                "error": f"Failed to initialize skill: {exc}",
            }

        supports_direct = bool(getattr(skill, "supports_direct_execution", False))
        if not supports_direct:
            return {
                "success": False,
                "status": "error",
                "skill": skill_name,
                "error": f"Skill {skill_name} does not support direct execution",
            }

        context = ExecutionContext(
            trigger_type=str(payload.get("trigger_type", "system_event")),
            user_id=payload.get("user_id"),
            query=payload.get("query"),
            params=payload,
            metadata={"source": "openclaw", "skill": skill_name},
        )

    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(captured_stderr):
            if hasattr(skill, "run") and callable(getattr(skill, "run")):
                result = skill.run(context=context.to_dict(), auto_notify=False)
            else:
                execute = getattr(skill, "execute")
                signature = inspect.signature(execute)
                if "context" in signature.parameters:
                    result = execute(context=context.to_dict())
                else:
                    result = execute(**payload)
    except Exception as exc:
        return {
            "success": False,
            "status": "error",
            "skill": skill_name,
            "error": str(exc),
            "stderr": captured_stderr.getvalue().strip() or None,
        }

    normalized = _normalize_result(result)
    captured = {
        "setup_stdout": setup_stdout.getvalue().strip(),
        "setup_stderr": setup_stderr.getvalue().strip(),
        "stdout": captured_stdout.getvalue().strip(),
        "stderr": captured_stderr.getvalue().strip(),
    }
    captured = {k: v for k, v in captured.items() if v}
    if captured:
        normalized.setdefault("debug", {})
        normalized["debug"]["captured_output"] = captured
    normalized["skill"] = skill_name
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Run skill directly without agent reasoning.")
    parser.add_argument("--skill", required=True, help="Skill name, e.g. video_monitor_skill")
    parser.add_argument("--payload", default="{}", help="JSON payload")
    args = parser.parse_args()

    payload = _parse_payload(args.payload)
    if "_payload_parse_error" in payload:
        return _json_out(
            {
                "success": False,
                "status": "error",
                "skill": args.skill,
                "error": f"Invalid payload JSON: {payload['_payload_parse_error']}",
            },
            exit_code=1,
        )

    result = _execute_skill(args.skill, payload)
    return _json_out(result, exit_code=0 if result.get("success") else 1)


if __name__ == "__main__":
    raise SystemExit(main())
