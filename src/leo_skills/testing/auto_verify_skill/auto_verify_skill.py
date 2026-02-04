# -*- coding: utf-8 -*-
"""
auto_verify_skill - 自动验证技能

自动验证任务执行结果，支持多种验证方式：
- 文件存在性验证
- 内容匹配验证
- 执行结果验证
- 回归测试验证
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum


class VerifyType(Enum):
    """验证类型"""
    FILE_EXISTS = "file_exists"
    CONTENT_MATCH = "content_match"
    COMMAND_OUTPUT = "command_output"
    JSON_SCHEMA = "json_schema"
    CUSTOM = "custom"


class VerifyStatus(Enum):
    """验证状态"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class VerifyRule:
    """验证规则"""
    name: str
    verify_type: str
    target: str
    expected: Any
    operator: str = "equals"  # equals, contains, regex, gt, lt, etc.
    description: str = ""


@dataclass
class VerifyResult:
    """验证结果"""
    rule_name: str
    status: VerifyStatus
    actual: Any = None
    expected: Any = None
    message: str = ""
    duration_ms: float = 0.0


class AutoVerifySkill:
    """
    自动验证技能 - 自动化验证任务结果

    功能：
    - 文件存在性检查
    - 内容匹配验证
    - 命令输出验证
    - JSON Schema 验证
    - 自定义验证逻辑

    适用场景：
    - 代码生成后的验证
    - 配置更新后的检查
    - 任务完成的确认
    - CI/CD 流水线集成
    """

    def __init__(self):
        self.name = "auto_verify_skill"
        self.version = "1.0.0"
        self.description = "自动验证技能 - 多维度结果验证"
        self.results: List[VerifyResult] = []

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            action: 动作类型 (verify/batch/report)
            rules: 验证规则列表
            rule: 单条验证规则
            stop_on_failure: 失败时是否停止

        Returns:
            Dict 包含验证结果
        """
        action = kwargs.get("action", "verify")

        try:
            if action == "verify":
                result = self.verify(
                    rule=kwargs.get("rule", {})
                )
            elif action == "batch":
                result = self.verify_batch(
                    rules=kwargs.get("rules", []),
                    stop_on_failure=kwargs.get("stop_on_failure", False)
                )
            elif action == "report":
                result = self.generate_report()
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

    def verify(self, rule: Dict[str, Any]) -> VerifyResult:
        """
        执行单条验证

        Args:
            rule: 验证规则字典

        Returns:
            VerifyResult 验证结果
        """
        import time
        start_time = time.time()

        verify_type = rule.get("type", "custom")
        target = rule.get("target", "")
        expected = rule.get("expected")
        operator = rule.get("operator", "equals")

        try:
            if verify_type == VerifyType.FILE_EXISTS.value:
                actual = os.path.exists(target)
                passed = actual == expected

            elif verify_type == VerifyType.CONTENT_MATCH.value:
                file_path = rule.get("file")
                if not file_path or not os.path.exists(file_path):
                    result = VerifyResult(
                        rule_name=rule.get("name", "unnamed"),
                        status=VerifyStatus.ERROR,
                        message=f"文件不存在: {file_path}"
                    )
                    self.results.append(result)
                    return result

                content = Path(file_path).read_text(encoding="utf-8")
                actual = content

                if operator == "contains":
                    passed = expected in content
                elif operator == "regex":
                    passed = re.search(expected, content) is not None
                elif operator == "equals":
                    passed = content == expected
                else:
                    passed = False

            elif verify_type == VerifyType.COMMAND_OUTPUT.value:
                command = rule.get("command", target)
                import subprocess
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                actual = result.stdout.strip()

                if operator == "equals":
                    passed = actual == expected
                elif operator == "contains":
                    passed = expected in actual
                elif operator == "regex":
                    passed = re.search(expected, actual) is not None
                else:
                    passed = result.returncode == 0

            elif verify_type == VerifyType.JSON_SCHEMA.value:
                file_path = rule.get("file", target)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                schema = rule.get("schema", {})
                passed = self._validate_json_schema(data, schema)
                actual = data

            else:  # custom
                custom_func = rule.get("function")
                if callable(custom_func):
                    passed, actual = custom_func(target, expected)
                else:
                    passed = False
                    actual = None

            duration = (time.time() - start_time) * 1000

            result = VerifyResult(
                rule_name=rule.get("name", "unnamed"),
                status=VerifyStatus.PASSED if passed else VerifyStatus.FAILED,
                actual=actual,
                expected=expected,
                message="验证通过" if passed else f"验证失败: 期望值 {expected}, 实际值 {actual}",
                duration_ms=duration
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            result = VerifyResult(
                rule_name=rule.get("name", "unnamed"),
                status=VerifyStatus.ERROR,
                message=f"验证出错: {str(e)}",
                duration_ms=duration
            )

        self.results.append(result)
        return result

    def verify_batch(
        self,
        rules: List[Dict[str, Any]],
        stop_on_failure: bool = False
    ) -> Dict[str, Any]:
        """
        批量验证

        Args:
            rules: 验证规则列表
            stop_on_failure: 失败时是否停止

        Returns:
            Dict 包含批量验证结果
        """
        passed_count = 0
        failed_count = 0
        error_count = 0

        for rule in rules:
            result = self.verify(rule)

            if result.status == VerifyStatus.PASSED:
                passed_count += 1
            elif result.status == VerifyStatus.FAILED:
                failed_count += 1
                if stop_on_failure:
                    break
            else:
                error_count += 1
                if stop_on_failure:
                    break

        total = len(rules)
        success_rate = passed_count / total if total > 0 else 0

        return {
            "total": total,
            "passed": passed_count,
            "failed": failed_count,
            "error": error_count,
            "success_rate": f"{success_rate:.1%}",
            "all_passed": failed_count == 0 and error_count == 0,
            "results": [
                {
                    "rule": r.rule_name,
                    "status": r.status.value,
                    "message": r.message
                }
                for r in self.results[-len(rules):]
            ]
        }

    def _validate_json_schema(self, data: Any, schema: Dict) -> bool:
        """简单JSON Schema验证"""
        if not isinstance(schema, dict):
            return True

        schema_type = schema.get("type")
        if schema_type == "object":
            if not isinstance(data, dict):
                return False
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            for key in required:
                if key not in data:
                    return False
            return True
        elif schema_type == "array":
            if not isinstance(data, list):
                return False
            return True
        elif schema_type == "string":
            return isinstance(data, str)
        elif schema_type == "number":
            return isinstance(data, (int, float))
        elif schema_type == "boolean":
            return isinstance(data, bool)

        return True

    def generate_report(self) -> Dict[str, Any]:
        """
        生成验证报告

        Returns:
            Dict 包含验证报告
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == VerifyStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == VerifyStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == VerifyStatus.ERROR)

        total_duration = sum(r.duration_ms for r in self.results)

        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "success_rate": f"{passed/total:.1%}" if total > 0 else "N/A",
                "total_duration_ms": round(total_duration, 2)
            },
            "details": [
                {
                    "rule": r.rule_name,
                    "status": r.status.value,
                    "message": r.message,
                    "duration_ms": round(r.duration_ms, 2)
                }
                for r in self.results
            ]
        }

    def create_file_rule(
        self,
        name: str,
        file_path: str,
        should_exist: bool = True
    ) -> Dict[str, Any]:
        """创建文件存在性验证规则"""
        return {
            "name": name,
            "type": VerifyType.FILE_EXISTS.value,
            "target": file_path,
            "expected": should_exist
        }

    def create_content_rule(
        self,
        name: str,
        file_path: str,
        expected_content: str,
        operator: str = "contains"
    ) -> Dict[str, Any]:
        """创建内容匹配验证规则"""
        return {
            "name": name,
            "type": VerifyType.CONTENT_MATCH.value,
            "file": file_path,
            "target": expected_content,
            "expected": expected_content,
            "operator": operator
        }

    def create_command_rule(
        self,
        name: str,
        command: str,
        expected_output: str = "",
        operator: str = "equals"
    ) -> Dict[str, Any]:
        """创建命令输出验证规则"""
        return {
            "name": name,
            "type": VerifyType.COMMAND_OUTPUT.value,
            "command": command,
            "target": command,
            "expected": expected_output,
            "operator": operator
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "verify_types": [t.value for t in VerifyType],
            "operators": ["equals", "contains", "regex", "gt", "lt"],
            "features": [
                "single_verify",
                "batch_verify",
                "file_exists",
                "content_match",
                "command_output",
                "json_schema"
            ]
        }


# 向后兼容
Auto_Verify_Skill = AutoVerifySkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Auto Verify Skill - 演示")
    print("=" * 60)

    skill = AutoVerifySkill()

    # 演示1: 文件存在性验证
    print("\n1. 文件存在性验证")
    print("-" * 40)
    rule = skill.create_file_rule(
        name="检查配置文件",
        file_path="src/leo_config/settings/config.yaml",
        should_exist=True
    )
    result = skill.verify(rule)
    print(f"规则: {result.rule_name}")
    print(f"状态: {result.status.value}")
    print(f"消息: {result.message}")

    # 演示2: 内容匹配验证
    print("\n2. 内容匹配验证")
    print("-" * 40)
    rule = skill.create_content_rule(
        name="检查版本号",
        file_path="README.md",
        expected_content="Leo",
        operator="contains"
    )
    result = skill.verify(rule)
    print(f"规则: {result.rule_name}")
    print(f"状态: {result.status.value}")

    # 演示3: 命令输出验证
    print("\n3. 命令输出验证")
    print("-" * 40)
    rule = skill.create_command_rule(
        name="检查Python版本",
        command="python --version",
        expected_output="Python",
        operator="contains"
    )
    result = skill.verify(rule)
    print(f"规则: {result.rule_name}")
    print(f"状态: {result.status.value}")
    print(f"输出: {result.actual}")

    # 演示4: 批量验证
    print("\n4. 批量验证")
    print("-" * 40)
    rules = [
        skill.create_file_rule("检查README", "README.md", True),
        skill.create_content_rule("检查配置", "CLAUDE.md", "Leo", "contains"),
    ]
    result = skill.verify_batch(rules, stop_on_failure=False)
    print(f"总计: {result['total']}")
    print(f"通过: {result['passed']}")
    print(f"成功率: {result['success_rate']}")

    # 演示5: 生成报告
    print("\n5. 验证报告")
    print("-" * 40)
    report = skill.generate_report()
    print(f"总验证数: {report['summary']['total']}")
    print(f"成功率: {report['summary']['success_rate']}")
    print(f"总耗时: {report['summary']['total_duration_ms']}ms")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
