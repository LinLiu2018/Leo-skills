"""Output manager for executor-style skills."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import hmac
import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional
from urllib import request


@dataclass
class OutputTarget:
    """Single output destination."""

    type: str
    config: Dict[str, Any] = field(default_factory=dict)


class OutputManager:
    """Dispatches skill results to file/feishu/database."""

    def __init__(self) -> None:
        self.targets: List[OutputTarget] = []

    def to_file(self, path: str, fmt: str = "json", append: bool = False) -> OutputTarget:
        target = OutputTarget(
            type="file",
            config={"path": path, "format": fmt.lower(), "append": append},
        )
        self.targets.append(target)
        return target

    def to_feishu(
        self,
        webhook: str,
        secret: Optional[str] = None,
        mention_all: bool = False,
    ) -> OutputTarget:
        target = OutputTarget(
            type="feishu",
            config={"webhook": webhook, "secret": secret, "mention_all": mention_all},
        )
        self.targets.append(target)
        return target

    def to_database(self, config: Dict[str, Any]) -> OutputTarget:
        db_path = config.get("db_path", "output/skills.db")
        table = config.get("table", "skill_output")
        target = OutputTarget(
            type="database",
            config={"db_path": db_path, "table": table},
        )
        self.targets.append(target)
        return target

    def dispatch(
        self,
        result: Any,
        context: Optional[Dict[str, Any]] = None,
        skill_name: str = "unknown_skill",
    ) -> List[Dict[str, Any]]:
        payload = {
            "skill_name": skill_name,
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "result": self._normalize_result(result),
        }
        statuses: List[Dict[str, Any]] = []
        for target in self.targets:
            try:
                if target.type == "file":
                    self._dispatch_file(payload, target.config)
                elif target.type == "feishu":
                    self._dispatch_feishu(payload, target.config)
                elif target.type == "database":
                    self._dispatch_database(payload, target.config)
                statuses.append({"type": target.type, "success": True})
            except Exception as exc:  # pragma: no cover - best effort sinks
                statuses.append(
                    {"type": target.type, "success": False, "error": str(exc)}
                )
        return statuses

    def _dispatch_file(self, payload: Dict[str, Any], config: Dict[str, Any]) -> None:
        target_path = Path(config["path"])
        target_path.parent.mkdir(parents=True, exist_ok=True)
        fmt = config.get("format", "json")
        append = bool(config.get("append"))

        if fmt == "json":
            mode = "a" if append else "w"
            with target_path.open(mode, encoding="utf-8") as handle:
                if append:
                    handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
                else:
                    json.dump(payload, handle, ensure_ascii=False, indent=2)
            return

        text = self._as_text(payload)
        mode = "a" if append else "w"
        with target_path.open(mode, encoding="utf-8") as handle:
            handle.write(text + ("\n" if append else ""))

    def _dispatch_feishu(self, payload: Dict[str, Any], config: Dict[str, Any]) -> None:
        webhook = config["webhook"]
        message = self._as_text(payload)
        card = {"msg_type": "text", "content": {"text": message}}
        if config.get("mention_all"):
            card["content"]["text"] = f"<at user_id=\"all\"></at>\n{message}"

        secret = config.get("secret")
        if secret:
            timestamp = str(int(datetime.now().timestamp()))
            sign = self._sign_feishu(timestamp, secret)
            webhook = f"{webhook}&timestamp={timestamp}&sign={sign}"

        data = json.dumps(card, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            webhook,
            data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with request.urlopen(req, timeout=10):
            return

    def _dispatch_database(self, payload: Dict[str, Any], config: Dict[str, Any]) -> None:
        db_path = Path(config.get("db_path", "output/skills.db"))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        table = config.get("table", "skill_output")

        with sqlite3.connect(db_path) as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    context_json TEXT,
                    result_json TEXT
                )
                """
            )
            conn.execute(
                f"""
                INSERT INTO {table} (skill_name, timestamp, context_json, result_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    payload["skill_name"],
                    payload["timestamp"],
                    json.dumps(payload.get("context", {}), ensure_ascii=False),
                    json.dumps(payload.get("result", {}), ensure_ascii=False),
                ),
            )
            conn.commit()

    def _normalize_result(self, result: Any) -> Any:
        if hasattr(result, "to_dict") and callable(result.to_dict):
            return result.to_dict()
        return result

    def _as_text(self, payload: Dict[str, Any]) -> str:
        return (
            f"[{payload['timestamp']}] {payload['skill_name']}\n"
            f"Context: {json.dumps(payload.get('context', {}), ensure_ascii=False)}\n"
            f"Result: {json.dumps(payload.get('result', {}), ensure_ascii=False)}"
        )

    def _sign_feishu(self, timestamp: str, secret: str) -> str:
        string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
        key = secret.encode("utf-8")
        digest = hmac.new(key, string_to_sign, digestmod=hashlib.sha256).digest()
        return base64.b64encode(digest).decode("utf-8")
