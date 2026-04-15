# -*- coding: utf-8 -*-
"""
Security Scan Skill - AI Agent安全扫描工具
==========================================

参考 everything-claude-code 的 AgentShield 设计
提供代码安全扫描和漏洞检测能力

Author: Leo AI System
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from base import BaseSkill, SkillResult


@dataclass
class SecurityFinding:
    """安全问题发现"""
    severity: str  # critical, high, medium, low, info
    category: str  # injection, sensitive_data, path_traversal, etc.
    file: str
    line: int
    code_snippet: str
    description: str
    cwe_id: Optional[str] = None
    fix_suggestion: Optional[str] = None


class SecurityScanSkill(BaseSkill):
    """
    Security Scan Skill

    提供代码安全扫描和漏洞检测
    """

    # 敏感信息正则模式
    SENSITIVE_PATTERNS = [
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}', "API Key泄露", "critical"),
        (r'secret[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}', "Secret Key泄露", "critical"),
        (r'password["\']?\s*[:=]\s*["\']?[^"\s]{8,}', "硬编码密码", "critical"),
        (r'token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}', "Token泄露", "high"),
        (r'aws[_-]?access[_-]?key["\']?\s*[:=]\s*["\']?[A-Z0-9]{20,}', "AWS Access Key", "critical"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token", "critical"),
        (r'xox[baprs]-[a-zA-Z0-9]{10,}', "Slack Token", "high"),
    ]

    # 命令注入风险模式
    INJECTION_PATTERNS = [
        (r'os\.system\s*\(', "os.system命令注入风险", "high"),
        (r'subprocess\.(call|run|popen|spawn)\s*\([^)]*\bexec\b', "subprocess命令注入风险", "high"),
        (r'eval\s*\(', "eval代码执行风险", "critical"),
        (r'exec\s*\(', "exec代码执行风险", "critical"),
        (r'os\.popen\s*\(', "os.popen命令注入风险", "medium"),
    ]

    # 路径遍历模式
    PATH_TRAVERSAL_PATTERNS = [
        (r'\.\./', "路径遍历: ..", "medium"),
        (r'\.\.\\', "路径遍历: ..\\", "medium"),
        (r'open\s*\([^)]*\+[^)]*\.\.[^)]*\)', "动态路径遍历", "medium"),
    ]

    # SQL注入风险模式
    SQL_INJECTION_PATTERNS = [
        (r'execute\s*\([^)]*\+[^)]*(?:SELECT|INSERT|UPDATE|DELETE|DROP)', "SQL拼接注入风险", "high"),
        (r'cursor\.execute\s*\([^)]*%s[^)]*\+', "SQL格式化注入风险", "high"),
        (r'''["\']SELECT[^)]*[\'"]\s*\+''', "SQL字符串拼接", "high"),
    ]

    @property
    def name(self) -> str:
        return "security_scan"

    @property
    def description(self) -> str:
        return "AI Agent安全扫描工具 - 漏洞检测和风险评估"

    def execute(self, action: str = "default", **kwargs) -> SkillResult:
        """
        执行安全扫描

        Actions:
            default: 完整扫描
            quick: 快速扫描
            fix: 尝试自动修复
        """
        scan_path = kwargs.get("path", "src")
        quick = kwargs.get("quick", False)

        if action == "fix":
            return self._auto_fix()
        elif quick or action == "quick":
            return self._quick_scan(scan_path)
        else:
            return self._full_scan(scan_path)

    def _full_scan(self, scan_path: str) -> SkillResult:
        """完整安全扫描"""
        findings = []
        scanned_files = 0

        scan_dir = Path(scan_path)
        if not scan_dir.exists():
            return SkillResult.fail(f"扫描路径不存在: {scan_path}")

        for file_path in scan_dir.rglob("*.py"):
            if self._should_skip(file_path):
                continue

            try:
                file_findings = self._scan_file(file_path)
                findings.extend(file_findings)
                scanned_files += 1
            except Exception as e:
                pass

        # 按严重性排序
        findings.sort(key=lambda f: self._severity_weight(f.severity), reverse=True)

        # 汇总
        summary = self._summarize_findings(findings)

        return SkillResult.ok(
            data={
                "findings": [f.__dict__ for f in findings],
                "summary": summary,
                "scanned_files": scanned_files,
                "timestamp": datetime.now().isoformat()
            },
            message=f"扫描完成 | 高危: {summary['critical'] + summary['high']}, 中危: {summary['medium']}, 低危: {summary['low']}"
        )

    def _quick_scan(self, scan_path: str) -> SkillResult:
        """快速扫描 - 只检查关键模式"""
        findings = []

        scan_dir = Path(scan_path)
        for file_path in list(scan_dir.rglob("*.py"))[:20]:  # 最多20个文件
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                # 只检查敏感信息
                for pattern, desc, severity in self.SENSITIVE_PATTERNS:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        line_num = content[:match.start()].count("\n") + 1
                        findings.append(SecurityFinding(
                            severity=severity,
                            category="sensitive_data",
                            file=str(file_path),
                            line=line_num,
                            code_snippet=match.group(),
                            description=desc,
                            cwe_id="CWE-798" if severity == "critical" else None
                        ))
            except:
                pass

        summary = self._summarize_findings(findings)

        return SkillResult.ok(
            data={
                "findings": [f.__dict__ for f in findings],
                "summary": summary,
                "quick_scan": True
            },
            message=f"快速扫描完成 | 发现 {len(findings)} 个问题"
        )

    def _scan_file(self, file_path: Path) -> List[SecurityFinding]:
        """扫描单个文件"""
        findings = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
        except:
            return findings

        for line_num, line in enumerate(lines, 1):
            # 跳过注释和字符串
            if line.strip().startswith("#") or line.strip().startswith('"""') or line.strip().startswith("'''"):
                continue

            # 检查敏感信息
            for pattern, desc, severity in self.SENSITIVE_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        severity=severity,
                        category="sensitive_data",
                        file=str(file_path),
                        line=line_num,
                        code_snippet=line.strip()[:100],
                        description=desc,
                        cwe_id="CWE-798" if "key" in desc.lower() else "CWE-312"
                    ))

            # 检查命令注入
            for pattern, desc, severity in self.INJECTION_PATTERNS:
                if re.search(pattern, line):
                    findings.append(SecurityFinding(
                        severity=severity,
                        category="injection",
                        file=str(file_path),
                        line=line_num,
                        code_snippet=line.strip()[:100],
                        description=desc,
                        cwe_id="CWE-78" if "command" in desc.lower() else "CWE-94"
                    ))

            # 检查路径遍历
            for pattern, desc, severity in self.PATH_TRAVERSAL_PATTERNS:
                if re.search(pattern, line):
                    findings.append(SecurityFinding(
                        severity=severity,
                        category="path_traversal",
                        file=str(file_path),
                        line=line_num,
                        code_snippet=line.strip()[:100],
                        description=desc,
                        cwe_id="CWE-22"
                    ))

        return findings

    def _auto_fix(self) -> SkillResult:
        """自动修复 - 标记问题但不自动修改"""
        return SkillResult.ok(
            data={"message": "自动修复需要人工确认，请查看扫描结果后手动修复"},
            message="安全修复建议已生成"
        )

    def _should_skip(self, file_path: Path) -> bool:
        """判断是否跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            "node_modules",
            ".git",
            "venv",
            "env",
            "dist",
            "build"
        ]
        return any(p in str(file_path) for p in skip_patterns)

    def _severity_weight(self, severity: str) -> int:
        """严重性权重"""
        weights = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
        return weights.get(severity, 0)

    def _summarize_findings(self, findings: List[SecurityFinding]) -> Dict[str, int]:
        """汇总发现"""
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            if f.severity in summary:
                summary[f.severity] += 1
        return summary

    def get_actions(self) -> List[str]:
        return ["default", "quick", "fix"]


# 快捷函数
def run_security_scan(**kwargs) -> Dict[str, Any]:
    """运行安全扫描"""
    skill = SecurityScanSkill()
    result = skill.execute(**kwargs)
    return result.to_dict()


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "src"
    result = run_security_scan(scan_path=path)
    print(json.dumps(result, ensure_ascii=False, indent=2))