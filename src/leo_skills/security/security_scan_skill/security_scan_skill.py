"""
安全扫描技能

扫描代码中的安全隐患，包括硬编码密钥、SQL 注入、XSS 跨站脚本、
命令注入、不安全随机数、调试模式启用、不安全 HTTP 连接等。
输出 Markdown 格式的安全报告。
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern

from leo_skills.core.base_executor import BaseExecutor

logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """安全问题记录。"""
    rule_id: str
    severity: str         # critical / high / medium / low
    title: str
    description: str
    file_path: str
    line_number: int
    line_content: str
    suggestion: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id, "severity": self.severity,
            "title": self.title, "description": self.description,
            "file": self.file_path, "line": self.line_number,
            "content": self.line_content[:200], "suggestion": self.suggestion,
        }


@dataclass
class ScanRule:
    """扫描规则定义。"""
    rule_id: str
    severity: str
    title: str
    description: str
    pattern: Pattern
    file_types: List[str]    # 限定文件扩展名（空列表表示全部）
    suggestion: str
    exclude_patterns: List[str] = field(default_factory=list)  # 排除误报的模式


# 预置规则集
_RULES: List[ScanRule] = [
    ScanRule(
        rule_id="SEC001", severity="high", title="硬编码密钥",
        description="检测到疑似硬编码的 API 密钥、密码或 Token",
        pattern=re.compile(
            r"""(?:api[_-]?key|secret[_-]?key|password|token|auth[_-]?token|access[_-]?token)"""
            r"""\s*[=:]\s*['\"][A-Za-z0-9+/=_\-]{16,}['\"]""",
            re.IGNORECASE,
        ),
        file_types=[".py", ".js", ".ts", ".json", ".yaml", ".yml", ".env", ".cfg", ".ini"],
        suggestion="将密钥移到环境变量或 .env 文件中，使用 os.environ.get() 读取",
        exclude_patterns=["example", "template", "placeholder", "your-", "xxx", "test"],
    ),
    ScanRule(
        rule_id="SEC002", severity="critical", title="SQL 注入风险",
        description="检测到字符串拼接方式构建 SQL 语句",
        pattern=re.compile(
            r"""(?:execute|cursor\.execute|raw|query)\s*\(\s*(?:f['\"]|['\"].*?%s|['\"].*?\+|.*?\.format)""",
            re.IGNORECASE,
        ),
        file_types=[".py"],
        suggestion="使用参数化查询: cursor.execute('SELECT * FROM t WHERE id = %s', (id,))",
    ),
    ScanRule(
        rule_id="SEC003", severity="high", title="XSS 跨站脚本风险",
        description="检测到未转义的用户输入直接插入 HTML",
        pattern=re.compile(
            r"""(?:innerHTML|outerHTML|document\.write|v-html)\s*[=]\s*""",
            re.IGNORECASE,
        ),
        file_types=[".js", ".ts", ".jsx", ".tsx", ".vue", ".html"],
        suggestion="使用 textContent 替代 innerHTML，或使用模板引擎的自动转义功能",
    ),
    ScanRule(
        rule_id="SEC004", severity="critical", title="命令注入风险",
        description="检测到直接将变量拼接到系统命令中",
        pattern=re.compile(
            r"""(?:os\.system|os\.popen|subprocess\.call|subprocess\.run|subprocess\.Popen)\s*\(\s*(?:f['\"]|.*?\+|.*?\.format|.*?%\s)""",
            re.IGNORECASE,
        ),
        file_types=[".py"],
        suggestion="使用 subprocess.run() 的列表参数形式，避免 shell=True",
    ),
    ScanRule(
        rule_id="SEC005", severity="medium", title="不安全随机数",
        description="使用 random 模块生成安全相关的随机数",
        pattern=re.compile(
            r"""(?:random\.random|random\.randint|random\.choice|random\.uniform)\s*\(""",
            re.IGNORECASE,
        ),
        file_types=[".py"],
        suggestion="安全场景请使用 secrets 模块: secrets.token_hex(), secrets.randbelow()",
        exclude_patterns=["test", "mock", "demo", "example"],
    ),
    ScanRule(
        rule_id="SEC006", severity="low", title="调试模式启用",
        description="检测到生产环境可能启用了调试模式",
        pattern=re.compile(
            r"""(?:DEBUG\s*=\s*True|debug\s*=\s*True|app\.run\(.*?debug\s*=\s*True)""",
            re.IGNORECASE,
        ),
        file_types=[".py", ".env", ".cfg"],
        suggestion="生产环境务必关闭调试模式: DEBUG = False",
    ),
    ScanRule(
        rule_id="SEC007", severity="medium", title="不安全 HTTP 连接",
        description="检测到使用 HTTP（非 HTTPS）的 URL",
        pattern=re.compile(r"""['\"]http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[^\s'\"]+['\"]"""),
        file_types=[".py", ".js", ".ts", ".json", ".yaml", ".yml"],
        suggestion="使用 HTTPS 替代 HTTP 以确保传输安全",
        exclude_patterns=["example", "localhost", "test"],
    ),
    ScanRule(
        rule_id="SEC008", severity="high", title="eval/exec 使用",
        description="检测到使用 eval() 或 exec() 执行动态代码",
        pattern=re.compile(r"""(?:^|\s)(?:eval|exec)\s*\(""", re.MULTILINE),
        file_types=[".py"],
        suggestion="避免使用 eval/exec，改用 ast.literal_eval() 或其他安全替代方案",
    ),
    ScanRule(
        rule_id="SEC009", severity="medium", title="敏感文件暴露",
        description="检测到可能被提交到版本控制的敏感文件",
        pattern=re.compile(r"""(?:\.env|credentials|secrets|private[_-]?key)""", re.IGNORECASE),
        file_types=[],  # 检查文件名
        suggestion="将敏感文件添加到 .gitignore 中",
    ),
    ScanRule(
        rule_id="SEC010", severity="high", title="CORS 全放开",
        description="检测到 CORS 配置为允许所有来源",
        pattern=re.compile(
            r"""(?:allow_origins\s*=\s*\[?\s*['\"]?\*['\"]?\s*\]?|Access-Control-Allow-Origin.*?\*)""",
            re.IGNORECASE,
        ),
        file_types=[".py", ".js", ".ts"],
        suggestion="限制 CORS 来源为特定域名列表",
    ),
]

# 扫描时排除的目录
_EXCLUDE_DIRS = {
    ".git", "__pycache__", "node_modules", "venv", ".venv", "env",
    ".pytest_cache", ".mypy_cache", "dist", "build", ".next",
    ".claude", ".mcp",
}


class SecurityScan(BaseExecutor):
    """代码安全扫描技能。

    支持的操作：
        - scan:   扫描指定目录
        - report: 扫描并生成 Markdown 报告
    """

    def __init__(self) -> None:
        self.name = "security_scan_skill"

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "scan",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        if action in ("scan", "run"):
            return self._action_scan(params)
        elif action == "report":
            return self._action_report(params)
        else:
            return {"status": "error", "message": f"未知操作: {action}"}

    # ------------------------------------------------------------------ #
    #  扫描
    # ------------------------------------------------------------------ #

    def _action_scan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        target = params.get("target", params.get("path", "."))
        max_file_size = params.get("max_file_size_kb", 500) * 1024

        issues = self.scan_directory(target, max_file_size)

        # 按严重程度统计
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        return {
            "status": "success",
            "action": "scan",
            "target": target,
            "total_issues": len(issues),
            "severity_counts": severity_counts,
            "issues": [i.to_dict() for i in issues],
        }

    def _action_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        target = params.get("target", params.get("path", "."))
        output_path = params.get("output", "security_report.md")
        max_file_size = params.get("max_file_size_kb", 500) * 1024

        issues = self.scan_directory(target, max_file_size)
        report = self._generate_report(issues, target)

        Path(output_path).write_text(report, encoding="utf-8")

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        return {
            "status": "success",
            "action": "report",
            "report_path": output_path,
            "total_issues": len(issues),
            "severity_counts": severity_counts,
        }

    # ------------------------------------------------------------------ #
    #  核心扫描逻辑
    # ------------------------------------------------------------------ #

    def scan_directory(self, target: str, max_file_size: int = 512000) -> List[SecurityIssue]:
        """扫描目录中的所有文件。"""
        target_path = Path(target)
        if not target_path.exists():
            logger.error(f"目标路径不存在: {target}")
            return []

        all_issues: List[SecurityIssue] = []

        if target_path.is_file():
            all_issues.extend(self._scan_file(target_path))
        else:
            for root, dirs, files in os.walk(target_path):
                # 排除目录
                dirs[:] = [d for d in dirs if d not in _EXCLUDE_DIRS]

                for fname in files:
                    fpath = Path(root) / fname
                    # 跳过过大文件
                    try:
                        if fpath.stat().st_size > max_file_size:
                            continue
                    except OSError:
                        continue

                    issues = self._scan_file(fpath)
                    all_issues.extend(issues)

        # 按严重程度排序
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_issues.sort(key=lambda x: severity_order.get(x.severity, 4))

        logger.info(f"扫描完成: 共发现 {len(all_issues)} 个安全问题")
        return all_issues

    def _scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """扫描单个文件。"""
        issues: List[SecurityIssue] = []
        ext = file_path.suffix.lower()

        # 检查文件名规则（SEC009）
        for rule in _RULES:
            if rule.rule_id == "SEC009":
                fname_lower = file_path.name.lower()
                if rule.pattern.search(fname_lower):
                    # 排除 .gitignore 本身
                    if file_path.name != ".gitignore":
                        issues.append(SecurityIssue(
                            rule_id=rule.rule_id, severity=rule.severity,
                            title=rule.title, description=rule.description,
                            file_path=str(file_path), line_number=0,
                            line_content=file_path.name,
                            suggestion=rule.suggestion,
                        ))

        # 读取文件内容
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return issues

        lines = content.split("\n")

        for rule in _RULES:
            if rule.rule_id == "SEC009":
                continue  # 文件名规则已处理

            # 检查文件类型是否匹配
            if rule.file_types and ext not in rule.file_types:
                continue

            for line_num, line in enumerate(lines, 1):
                if rule.pattern.search(line):
                    # 检查排除模式（减少误报）
                    line_lower = line.lower()
                    if any(ep in line_lower for ep in rule.exclude_patterns):
                        continue

                    issues.append(SecurityIssue(
                        rule_id=rule.rule_id, severity=rule.severity,
                        title=rule.title, description=rule.description,
                        file_path=str(file_path), line_number=line_num,
                        line_content=line.strip(),
                        suggestion=rule.suggestion,
                    ))

        return issues

    # ------------------------------------------------------------------ #
    #  报告生成
    # ------------------------------------------------------------------ #

    @staticmethod
    def _generate_report(issues: List[SecurityIssue], target: str) -> str:
        """生成 Markdown 格式的安全报告。"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for i in issues:
            severity_counts[i.severity] = severity_counts.get(i.severity, 0) + 1

        severity_labels = {
            "critical": "严重", "high": "高", "medium": "中", "low": "低"
        }

        lines = [
            f"# 安全扫描报告",
            f"\n**扫描目标**: `{target}`",
            f"**扫描时间**: {now}",
            f"**发现问题**: {len(issues)} 个\n",
            "## 问题概览\n",
            "| 严重程度 | 数量 |",
            "|---------|------|",
        ]
        for sev in ["critical", "high", "medium", "low"]:
            cnt = severity_counts.get(sev, 0)
            label = severity_labels[sev]
            lines.append(f"| {label} | {cnt} |")

        if not issues:
            lines.append("\n**未发现安全问题。**\n")
            return "\n".join(lines)

        lines.append("\n## 详细发现\n")

        for i, issue in enumerate(issues, 1):
            label = severity_labels.get(issue.severity, issue.severity)
            lines.extend([
                f"### {i}. [{label}] {issue.title} ({issue.rule_id})\n",
                f"- **文件**: `{issue.file_path}`",
                f"- **行号**: {issue.line_number}" if issue.line_number > 0 else "",
                f"- **描述**: {issue.description}",
                f"- **代码**: `{issue.line_content[:100]}`" if issue.line_content else "",
                f"- **修复建议**: {issue.suggestion}\n",
            ])

        lines.extend([
            "## 修复优先级建议\n",
            "1. 立即修复所有**严重**和**高**级别问题",
            "2. 在下一个迭代中处理**中**级别问题",
            "3. 规划处理**低**级别问题",
            f"\n---\n*由 Leo AI 安全扫描技能生成 | {now}*\n",
        ])

        return "\n".join(lines)


__all__ = ["SecurityScan"]
