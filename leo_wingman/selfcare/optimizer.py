"""
Optimizer routines for Wingman.
"""

from __future__ import annotations

from typing import Dict


def recommend_runtime_profile(error_rate: float, avg_latency_ms: float) -> Dict[str, str]:
    if error_rate > 0.2:
        return {"profile": "safe", "reason": "high_error_rate"}
    if avg_latency_ms > 3000:
        return {"profile": "fast", "reason": "high_latency"}
    return {"profile": "balanced", "reason": "nominal"}
