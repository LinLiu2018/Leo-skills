# -*- coding: utf-8 -*-
"""
code_verification_skill - 代码验证技能

验证代码质量和正确性，支持语法检查、风格检查、静态分析等。
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum

from leo_skills.core.base_executor import BaseExecutor


class CheckType(Enum):
    """检查类型"""
    SYNTAX = "syntax"           # 语法检查
    STYLE = "style"             # 代码风格
    COMPLEXITY = "complexity"   # 复杂度分析
    SECURITY = "security"       # 安全检查
    IMPORTS = "imports"         # 导入检查


class Severity(Enum):
    """问题严重程度"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CodeIssue:
    """代码问题"""
    line: int
    column: int
    severity: str
    check_type: str
    message: str
    suggestion: str = ""


@dataclass
class VerificationReport:
    """验证报告"""
    file_path: str
    total_lines: int
    issues: List[CodeIssue] = field(default_factory=list)
    score: float = 100.0


class CodeVerificationSkill(BaseExecutor):
    """
    代码验证技能 - 自动化代码质量检查

    功能：
    - 语法正确性检查
    - 代码风格检查
    - 复杂度分析
    - 安全漏洞扫描
    - 导入语句检查

    支持语言：
    - Python（完整支持）
    - JavaScript/TypeScript（基础支持）
    """

    def __init__(self):
        self.name = "code_verification_skill"
        self.version = "1.0.0"
        self.description = "代码验证技能 - 自动化质量检查"

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            action: 动作类型 (verify/file/batch)
            code: 代码内容
            file_path: 文件路径
            checks: 检查类型列表

        Returns:
            Dict 包含验证结果
        """
        action = kwargs.get("action", "verify")

        try:
            if action == "verify":
                result = self.verify_code(
                    code=kwargs.get("code", ""),
                    file_path=kwargs.get("file_path", "<string>"),
                    checks=kwargs.get("checks", [])
                )
            elif action == "file":
                result = self.verify_file(
                    file_path=kwargs.get("file_path", ""),
                    checks=kwargs.get("checks", [])
                )
            elif action == "batch":
                result = self.verify_batch(
                    file_paths=kwargs.get("file_paths", []),
                    checks=kwargs.get("checks", [])
                )
            else:
                return {
                    "status": "error",
                    "skill": self.name,
                    "error": f"Unknown action: {action}"
                }

            return {
                "status": "success",
                "skill": self.name,
                "action": action,
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "action": action,
                "error": str(e)
            }

    def verify_code(
        self,
        code: str,
        file_path: str = "<string>",
        checks: List[str] = None
    ) -> VerificationReport:
        """
        验证代码

        Args:
            code: 代码内容
            file_path: 文件路径（用于报告）
            checks: 检查类型列表

        Returns:
            VerificationReport 验证报告
        """
        if checks is None:
            checks = ["syntax", "style", "complexity"]

        issues = []
        total_lines = len(code.split('\n'))

        # 语法检查
        if "syntax" in checks:
            syntax_issues = self._check_syntax(code, file_path)
            issues.extend(syntax_issues)

        # 风格检查
        if "style" in checks:
            style_issues = self._check_style(code)
            issues.extend(style_issues)

        # 复杂度分析
        if "complexity" in checks:
            complexity_issues = self._check_complexity(code)
            issues.extend(complexity_issues)

        # 安全检查
        if "security" in checks:
            security_issues = self._check_security(code)
            issues.extend(security_issues)

        # 导入检查
        if "imports" in checks:
            import_issues = self._check_imports(code)
            issues.extend(import_issues)

        # 计算分数
        score = self._calculate_score(issues, total_lines)

        return VerificationReport(
            file_path=file_path,
            total_lines=total_lines,
            issues=issues,
            score=score
        )

    def verify_file(
        self,
        file_path: str,
        checks: List[str] = None
    ) -> VerificationReport:
        """
        验证文件

        Args:
            file_path: 文件路径
            checks: 检查类型列表

        Returns:
            VerificationReport 验证报告
        """
        path = Path(file_path)
        if not path.exists():
            return VerificationReport(
                file_path=file_path,
                total_lines=0,
                issues=[CodeIssue(
                    line=0, column=0,
                    severity=Severity.ERROR.value,
                    check_type="file",
                    message=f"文件不存在: {file_path}"
                )],
                score=0
            )

        code = path.read_text(encoding='utf-8')
        return self.verify_code(code, file_path, checks)

    def verify_batch(
        self,
        file_paths: List[str],
        checks: List[str] = None
    ) -> Dict[str, Any]:
        """
        批量验证

        Args:
            file_paths: 文件路径列表
            checks: 检查类型列表

        Returns:
            Dict 包含批量验证结果
        """
        reports = []
        total_issues = 0
        total_errors = 0
        total_warnings = 0

        for file_path in file_paths:
            report = self.verify_file(file_path, checks)
            reports.append({
                "file": report.file_path,
                "lines": report.total_lines,
                "score": report.score,
                "issue_count": len(report.issues)
            })
            total_issues += len(report.issues)
            total_errors += sum(1 for i in report.issues if i.severity == Severity.ERROR.value)
            total_warnings += sum(1 for i in report.issues if i.severity == Severity.WARNING.value)

        avg_score = sum(r.score for r in [self.verify_file(p, checks) for p in file_paths]) / len(file_paths) if file_paths else 100

        return {
            "total_files": len(file_paths),
            "total_issues": total_issues,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "average_score": round(avg_score, 2),
            "files": reports
        }

    def _check_syntax(self, code: str, file_path: str) -> List[CodeIssue]:
        """检查语法"""
        issues = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(CodeIssue(
                line=e.lineno or 1,
                column=e.offset or 0,
                severity=Severity.ERROR.value,
                check_type="syntax",
                message=f"语法错误: {e.msg}",
                suggestion="检查代码语法，确保括号匹配"
            ))
        return issues

    def _check_style(self, code: str) -> List[CodeIssue]:
        """检查代码风格"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # 行长度检查
            if len(line) > 120:
                issues.append(CodeIssue(
                    line=i,
                    column=120,
                    severity=Severity.WARNING.value,
                    check_type="style",
                    message=f"行长度超过120字符 ({len(line)})",
                    suggestion="考虑拆分行或提取变量"
                ))

            # 尾随空格
            if line.rstrip() != line:
                issues.append(CodeIssue(
                    line=i,
                    column=len(line),
                    severity=Severity.INFO.value,
                    check_type="style",
                    message="行尾有尾随空格",
                    suggestion="删除行尾空格"
                ))

            # Tab检查（应该使用空格）
            if '\t' in line:
                issues.append(CodeIssue(
                    line=i,
                    column=line.index('\t'),
                    severity=Severity.WARNING.value,
                    check_type="style",
                    message="使用了Tab缩进",
                    suggestion="使用4个空格代替Tab"
                ))

        return issues

    def _check_complexity(self, code: str) -> List[CodeIssue]:
        """检查复杂度"""
        issues = []
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 函数长度检查
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') and node.end_lineno else 0
                    if func_lines > 50:
                        issues.append(CodeIssue(
                            line=node.lineno,
                            column=0,
                            severity=Severity.WARNING.value,
                            check_type="complexity",
                            message=f"函数 '{node.name}' 过长 ({func_lines} 行)",
                            suggestion="考虑将函数拆分为多个小函数"
                        ))

                    # 参数数量检查
                    arg_count = len(node.args.args) + len(node.args.kwonlyargs)
                    if arg_count > 5:
                        issues.append(CodeIssue(
                            line=node.lineno,
                            column=0,
                            severity=Severity.WARNING.value,
                            check_type="complexity",
                            message=f"函数 '{node.name}' 参数过多 ({arg_count} 个)",
                            suggestion="考虑使用配置对象或参数对象"
                        ))

        except:
            pass  # 语法错误已经在语法检查中报告

        return issues

    def _check_security(self, code: str) -> List[CodeIssue]:
        """检查安全问题"""
        issues = []

        # 危险函数模式
        dangerous_patterns = [
            (r'eval\s*\(', "使用了 eval()", "避免使用 eval，考虑使用 ast.literal_eval 或其他安全方法"),
            (r'exec\s*\(', "使用了 exec()", "避免使用 exec，重构代码逻辑"),
            (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "使用 shell=True", "避免使用 shell=True，防止命令注入"),
            (r'input\s*\(', "使用 input()", "验证所有用户输入，防止注入攻击"),
        ]

        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, message, suggestion in dangerous_patterns:
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        line=i,
                        column=line.find('eval') if 'eval' in line else 0,
                        severity=Severity.WARNING.value,
                        check_type="security",
                        message=message,
                        suggestion=suggestion
                    ))

        return issues

    def _check_imports(self, code: str) -> List[CodeIssue]:
        """检查导入"""
        issues = []
        try:
            tree = ast.parse(code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")

            # 检查未使用的导入（简化检查，实际应该用更复杂的分析）
            # 这里只检查是否有导入
            if not imports and len(code.split('\n')) > 10:
                issues.append(CodeIssue(
                    line=1,
                    column=0,
                    severity=Severity.INFO.value,
                    check_type="imports",
                    message="文件没有导入任何模块",
                    suggestion="如果确实不需要导入，可以忽略此提示"
                ))

        except:
            pass

        return issues

    def _calculate_score(self, issues: List[CodeIssue], total_lines: int) -> float:
        """计算代码质量分数"""
        if total_lines == 0:
            return 0

        score = 100.0

        for issue in issues:
            if issue.severity == Severity.ERROR.value:
                score -= 10
            elif issue.severity == Severity.WARNING.value:
                score -= 3
            elif issue.severity == Severity.INFO.value:
                score -= 1

        # 根据行数调整（长文件更容有问题）
        if total_lines > 0:
            issue_ratio = len(issues) / total_lines
            score -= issue_ratio * 20

        return max(0, min(100, score))

    def format_report(self, report: VerificationReport) -> str:
        """格式化报告为字符串"""
        lines = [
            f"代码验证报告: {report.file_path}",
            f"总行数: {report.total_lines}",
            f"质量分数: {report.score:.1f}/100",
            f"发现问题: {len(report.issues)} 个",
            "-" * 60
        ]

        if report.issues:
            lines.append("")
            for issue in report.issues:
                lines.append(f"[{issue.severity.upper()}] 第{issue.line}行: {issue.message}")
                if issue.suggestion:
                    lines.append(f"  建议: {issue.suggestion}")
        else:
            lines.append("")
            lines.append("✓ 未发现问题！")

        return "\n".join(lines)

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "check_types": [t.value for t in CheckType],
            "severities": [s.value for s in Severity],
            "features": [
                "syntax_check",
                "style_check",
                "complexity_analysis",
                "security_scan",
                "import_check",
                "batch_verify"
            ]
        }


# 向后兼容
Code_Verification_Skill = CodeVerificationSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Code Verification Skill - 演示")
    print("=" * 60)

    skill = CodeVerificationSkill()

    # 演示1: 验证代码
    print("\n1. 代码验证（有问题）")
    print("-" * 40)
    bad_code = '''
def long_function(a,b,c,d,e,f,g):
    x = eval(input())
    if a:
        if b:
            if c:
                print("nested")
    return x
'''
    report = skill.verify_code(bad_code, "test.py", ["syntax", "style", "complexity", "security"])
    print(f"文件: {report.file_path}")
    print(f"行数: {report.total_lines}")
    print(f"分数: {report.score:.1f}/100")
    print(f"问题数: {len(report.issues)}")
    for issue in report.issues[:3]:
        print(f"  [{issue.severity}] 行{issue.line}: {issue.message}")

    # 演示2: 验证文件
    print("\n2. 验证实际文件")
    print("-" * 40)
    report = skill.verify_file("src/leo_skills/core/text_generator_skill/text_generator_skill.py")
    print(f"文件: {report.file_path}")
    print(f"分数: {report.score:.1f}/100")
    print(f"问题数: {len(report.issues)}")

    # 演示3: 格式化报告
    print("\n3. 格式化报告")
    print("-" * 40)
    simple_report = skill.verify_code("def test():\n    pass", "simple.py")
    formatted = skill.format_report(simple_report)
    print(formatted[:200] + "...")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
