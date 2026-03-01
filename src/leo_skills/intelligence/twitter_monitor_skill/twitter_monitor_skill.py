"""Twitter monitor skill wrapper with direct-execution support."""

from __future__ import annotations

from typing import Any, Dict, Optional

from leo_skills.base import SkillResult
from leo_skills.core.base_executor import BaseExecutor

_LEGACY_IMPORT_ERROR: Optional[str] = None
try:
    from .scripts.main import TwitterMonitor as _LegacyTwitterMonitor
except Exception as exc:  # pragma: no cover - optional runtime dependency
    _LegacyTwitterMonitor = None  # type: ignore[assignment]
    _LEGACY_IMPORT_ERROR = str(exc)


class TwitterMonitorSkill(BaseExecutor):
    """Direct-executable wrapper for Twitter monitoring."""

    supports_direct_execution = True
    default_schedule = "0 */6 * * *"

    def __init__(self, config_path: Optional[str] = None):
        self.name = "twitter_monitor_skill"
        self.display_name = "Twitter Monitor"
        self.version = "2.0.0"
        self._init_error: Optional[str] = _LEGACY_IMPORT_ERROR
        self._monitor: Optional[Any] = None
        if _LegacyTwitterMonitor is not None:
            try:
                self._monitor = _LegacyTwitterMonitor(config_path=config_path)
            except Exception as exc:
                self._init_error = str(exc)

    def execute(
        self,
        context: Optional[Dict[str, Any]] = None,
        action: str = "monitor",
        **kwargs,
    ) -> Any:
        params: Dict[str, Any] = {}
        if isinstance(context, dict):
            context_params = context.get("params")
            if isinstance(context_params, dict):
                params.update(context_params)
            params.update(context)
        if isinstance(kwargs.get("params"), dict):
            params.update(kwargs.pop("params"))
        params.update(kwargs)
        action = str(params.get("action", action))

        if self._init_error or self._monitor is None:
            result = {
                "status": "error",
                "success": False,
                "error": f"Twitter monitor init failed: {self._init_error or 'unknown error'}",
            }
            return self._direct_or_legacy(context, result, action)

        try:
            if action == "monitor":
                bloggers = params.get("bloggers")
                tweets = self._monitor.monitor(bloggers=bloggers if isinstance(bloggers, list) else None)
                result = {
                    "status": "success",
                    "success": True,
                    "action": action,
                    "tweet_count": len(tweets),
                    "data": tweets,
                }
            elif action == "search":
                keywords = params.get("keywords", [])
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(",") if k.strip()]
                max_results = int(params.get("max_results", 100))
                tweets = self._monitor.search_by_keywords(keywords=keywords, max_results=max_results)
                result = {
                    "status": "success",
                    "success": True,
                    "action": action,
                    "tweet_count": len(tweets),
                    "data": tweets,
                }
            elif action == "stats":
                stats = self._monitor.get_stats()
                result = {"status": "success", "success": True, "action": action, "data": stats}
            elif action == "unprocessed":
                limit = int(params.get("limit", 100))
                tweets = self._monitor.get_unprocessed_tweets(limit=limit)
                result = {
                    "status": "success",
                    "success": True,
                    "action": action,
                    "tweet_count": len(tweets),
                    "data": tweets,
                }
            elif action == "cleanup":
                days = int(params.get("days", 90))
                self._monitor.cleanup_old_tweets(days=days)
                result = {
                    "status": "success",
                    "success": True,
                    "action": action,
                    "message": f"cleanup completed (days={days})",
                }
            else:
                result = {"status": "error", "success": False, "error": f"Unknown action: {action}"}
        except Exception as exc:
            result = {"status": "error", "success": False, "error": str(exc)}

        return self._direct_or_legacy(context, result, action)

    def _direct_or_legacy(
        self,
        context: Optional[Dict[str, Any]],
        result: Dict[str, Any],
        action: str,
    ) -> Any:
        if context is None:
            return result
        if not result.get("success"):
            return SkillResult(success=False, data=result, error=result.get("error", "twitter monitor failed"))
        content = result.get("message") or f"Twitter monitor action '{action}' completed"
        markdown = (
            "## Twitter Monitor Result\n\n"
            f"- action: `{action}`\n"
            f"- success: `{result.get('success')}`\n"
            f"- tweet_count: `{result.get('tweet_count', 0)}`\n"
        )
        return SkillResult.ok(data=result, content=content, markdown=markdown)


# backward-compatible export
TwitterMonitor = _LegacyTwitterMonitor

__all__ = ["TwitterMonitorSkill", "TwitterMonitor"]
