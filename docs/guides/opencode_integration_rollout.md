# OpenCode Integration Rollout Guide

## Objective
Integrate `opencode-ai` workflows into `leo_ai_system` for internal company use first, then scale to mass promotion only after a measurable pilot passes.

This maps to the requirement document direction:
- full-chain AI operations
- content + lead + follow-up automation
- staged rollout with risk control

## What Was Implemented
- Bridge module: `src/leo_workflows/integrations/opencode_bridge.py`
- Runner script: `scripts/business/run_opencode_pilot.py`
- Default config: `config/opencode_internal_pilot.json`

## Why This Integration Path
`opencode-ai/main.py` currently calls `DirectorAgent.execute_workflow()`, but the referenced `DirectorAgent` does not implement that method in the current code snapshot.

To keep delivery unblocked, integration calls OpenCode workflow factories directly:
- `workflows.content_production`
- `workflows.lead_distribution`
- `workflows.followup_reminder`
- `workflows.effect_analysis`

This gives a stable path for internal validation now.

## Internal Pilot Flow
1. Run pilot workflows from config.
2. Collect per-workflow status and step outputs.
3. Apply scale gate:
- minimum success rate
- required workflow pass list
4. Produce GO / NO_GO decision.

## Commands
Run internal pilot:

```bash
python scripts/business/run_opencode_pilot.py --phase internal_pilot
```

Run scale assessment (latest pilot report):

```bash
python scripts/business/run_opencode_pilot.py --phase scale_assessment
```

Run scale assessment for a specific report:

```bash
python scripts/business/run_opencode_pilot.py --phase scale_assessment --pilot-report reports/integration/opencode_internal_pilot_YYYYMMDD_HHMMSS.json
```

## Output Artifacts
- Pilot report: `reports/integration/opencode_internal_pilot_*.json`
- Assessment report: `reports/integration/opencode_scale_assessment_*.json`

## Suggested Rollout Gates
Before mass promotion, require all:
- success_rate >= 0.85 for pilot workflows
- `content_production` passed
- `lead_distribution` passed
- `followup_reminder` passed
- no critical exceptions in step outputs

## Next Engineering Upgrades (After Pilot Pass)
1. Replace mock-like workflow internals with real platform APIs (Douyin/Video Account/Xiaohongshu/WeChat).
2. Add queue and retry strategy for multi-account concurrency.
3. Add cost monitoring for video generation and model calls.
4. Add compliance guardrails and rate limits per platform.
5. Build standardized onboarding package for external mass deployment.

