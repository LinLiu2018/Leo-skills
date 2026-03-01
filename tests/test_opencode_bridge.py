from leo_workflows.integrations.opencode_bridge import evaluate_scale_gate


def test_evaluate_scale_gate_go():
    results = [
        {"workflow_id": "content_production", "status": "completed"},
        {"workflow_id": "lead_distribution", "status": "completed"},
        {"workflow_id": "followup_reminder", "status": "completed"},
        {"workflow_id": "effect_analysis", "status": "failed"},
    ]
    gate = {
        "min_success_rate": 0.75,
        "required_workflows": [
            "content_production",
            "lead_distribution",
            "followup_reminder",
        ],
    }
    out = evaluate_scale_gate(results, gate)
    assert out["can_scale"] is True
    assert out["summary"] == "GO"


def test_evaluate_scale_gate_no_go_on_required_failure():
    results = [
        {"workflow_id": "content_production", "status": "completed"},
        {"workflow_id": "lead_distribution", "status": "failed"},
        {"workflow_id": "followup_reminder", "status": "completed"},
    ]
    gate = {
        "min_success_rate": 0.6,
        "required_workflows": ["lead_distribution"],
    }
    out = evaluate_scale_gate(results, gate)
    assert out["can_scale"] is False
    assert out["summary"] == "NO_GO"
    assert out["required_failures"] == ["lead_distribution"]

