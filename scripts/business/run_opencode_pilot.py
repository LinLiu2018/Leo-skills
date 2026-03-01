#!/usr/bin/env python3
"""
Run internal pilot integration against OpenCode workflows and evaluate scale readiness.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any, Dict, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from leo_workflows.integrations.opencode_bridge import (  # noqa: E402
    OpenCodeWorkflowBridge,
    evaluate_scale_gate,
)


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _latest_pilot_report(output_dir: Path) -> Optional[Path]:
    files = sorted(output_dir.glob("opencode_internal_pilot_*.json"))
    return files[-1] if files else None


def run_internal_pilot(config: Dict[str, Any], output_dir: Path) -> Path:
    opencode_root = config.get("opencode_root")
    if not opencode_root:
        raise ValueError("opencode_root missing in config")

    bridge = OpenCodeWorkflowBridge(opencode_root=opencode_root)
    results = bridge.run_internal_pilot(config)

    report = {
        "report_type": "internal_pilot",
        "generated_at": datetime.now().isoformat(),
        "company_profile": config.get("company_profile", {}),
        "results": results,
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"opencode_internal_pilot_{ts}.json"
    _save_json(report_path, report)
    return report_path


def run_scale_assessment(
    config: Dict[str, Any],
    output_dir: Path,
    pilot_report: Optional[Path],
) -> Path:
    report_path = pilot_report or _latest_pilot_report(output_dir)
    if report_path is None:
        raise FileNotFoundError("No pilot report found. Run internal_pilot first.")

    report = _load_json(report_path)
    workflow_results = report.get("results", {}).get("workflow_results", [])
    gate = evaluate_scale_gate(workflow_results, config.get("scale_gate", {}))

    assessment = {
        "report_type": "scale_assessment",
        "generated_at": datetime.now().isoformat(),
        "pilot_report": str(report_path),
        "gate_result": gate,
        "next_action": (
            "start_limited_rollout"
            if gate.get("can_scale")
            else "continue_internal_iteration"
        ),
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    assessment_path = output_dir / f"opencode_scale_assessment_{ts}.json"
    _save_json(assessment_path, assessment)
    return assessment_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenCode integration pilot runner")
    parser.add_argument(
        "--phase",
        choices=["internal_pilot", "scale_assessment"],
        default="internal_pilot",
        help="Execution phase",
    )
    parser.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "config" / "opencode_internal_pilot.json"),
        help="Path to integration config JSON",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "reports" / "integration"),
        help="Output directory for generated reports",
    )
    parser.add_argument(
        "--pilot-report",
        default="",
        help="Optional pilot report path for scale_assessment",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    config = _load_json(config_path)
    pilot_report = Path(args.pilot_report).resolve() if args.pilot_report else None

    if args.phase == "internal_pilot":
        report_path = run_internal_pilot(config, output_dir)
        report = _load_json(report_path)
        gate = report.get("results", {}).get("scale_gate_result", {})
        print(f"pilot_report={report_path}")
        print(f"go_no_go={gate.get('summary', 'NO_GO')}")
        print(f"success_rate={gate.get('success_rate', 0)}")
        return 0

    assessment_path = run_scale_assessment(config, output_dir, pilot_report)
    assessment = _load_json(assessment_path)
    gate = assessment.get("gate_result", {})
    print(f"assessment_report={assessment_path}")
    print(f"go_no_go={gate.get('summary', 'NO_GO')}")
    print(f"next_action={assessment.get('next_action', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
