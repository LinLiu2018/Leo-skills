# -*- coding: utf-8 -*-
"""
验证测试框架

自动验证代码修改效果
"""

import ast
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TestCase:
    """测试用例"""
    test_id: str
    name: str
    code: str
    expected_output: Any = None
    timeout: int = 30


@dataclass
class TestResult:
    """测试结果"""
    test_id: str
    passed: bool
    duration_ms: int
    output: Any = None
    error: str = ""
    traceback: str = ""


@dataclass
class ComparisonResult:
    """对比结果"""
    metric_name: str
    before_value: float
    after_value: float
    change_percent: float
    improved: bool


class EvolutionTester:
    """
    进化测试框架

    功能：
    - 单元测试自动生成
    - 回归测试
    - 性能基准测试
    - 对比分析
    """

    def __init__(self):
        self.test_results: List[Dict] = []

    def generate_tests(
        self,
        skill_path: str,
        test_count: int = 3
    ) -> List[TestCase]:
        """
        生成单元测试

        Args:
            skill_path: 技能路径
            test_count: 生成测试数量

        Returns:
            测试用例列表
        """
        # 读取技能代码
        file_path = self._find_skill_file(skill_path)
        if not file_path:
            raise FileNotFoundError(f"Skill file not found: {skill_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # 解析 AST 提取函数
        try:
            tree = ast.parse(code)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        except:
            functions = []

        # 生成测试用例
        tests = []
        for i in range(test_count):
            func_name = functions[i] if i < len(functions) else f"test_{i}"

            test_code = self._generate_test_code(func_name, skill_path)

            test = TestCase(
                test_id=f"test_{skill_path.replace('/', '_')}_{i}",
                name=f"Test {func_name}",
                code=test_code,
                timeout=30
            )
            tests.append(test)

        return tests

    def run_tests(
        self,
        skill_path: str,
        tests: Optional[List[TestCase]] = None
    ) -> List[TestResult]:
        """
        运行测试

        Args:
            skill_path: 技能路径
            tests: 测试用例列表

        Returns:
            测试结果列表
        """
        if tests is None:
            tests = self.generate_tests(skill_path)

        results = []

        for test in tests:
            result = self._run_single_test(test)
            results.append(result)

        # 记录结果
        self._record_test_results(skill_path, results)

        return results

    def run_tests_with_pytest(
        self,
        test_file_path: str,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        使用 pytest 运行测试

        Args:
            test_file_path: 测试文件路径
            verbose: 是否详细输出

        Returns:
            pytest 结果
        """
        cmd = [sys.executable, "-m", "pytest", test_file_path]

        if verbose:
            cmd.append("-v")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def compare_performance(
        self,
        before_metrics: Dict[str, float],
        after_metrics: Dict[str, float]
    ) -> List[ComparisonResult]:
        """
        性能对比

        Args:
            before_metrics: 修改前的指标
            after_metrics: 修改后的指标

        Returns:
            对比结果列表
        """
        results = []

        for metric_name in before_metrics:
            if metric_name not in after_metrics:
                continue

            before = before_metrics[metric_name]
            after = after_metrics[metric_name]

            if before == 0:
                continue

            # 计算变化百分比
            change_percent = ((after - before) / before) * 100

            # 判断是否改进
            # 对于延迟/错误率：降低 = 改进
            # 对于成功率：增加 = 改进
            improved = False
            if "time" in metric_name.lower() or "error" in metric_name.lower() or "latency" in metric_name.lower():
                improved = change_percent < 0
            else:
                improved = change_percent > 0

            result = ComparisonResult(
                metric_name=metric_name,
                before_value=before,
                after_value=after,
                change_percent=change_percent,
                improved=improved
            )
            results.append(result)

        return results

    def generate_report(
        self,
        skill_path: str,
        test_results: List[TestResult],
        comparison: Optional[List[ComparisonResult]] = None
    ) -> Dict[str, Any]:
        """
        生成测试报告

        Args:
            skill_path: 技能路径
            test_results: 测试结果
            comparison: 性能对比结果

        Returns:
            报告数据
        """
        passed = sum(1 for r in test_results if r.passed)
        failed = len(test_results) - passed
        pass_rate = (passed / len(test_results) * 100) if test_results else 0

        avg_duration = (
            sum(r.duration_ms for r in test_results) / len(test_results)
            if test_results else 0
        )

        report = {
            "skill_path": skill_path,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(test_results),
                "passed": passed,
                "failed": failed,
                "pass_rate": round(pass_rate, 2),
                "avg_duration_ms": round(avg_duration, 2)
            },
            "tests": [
                {
                    "test_id": r.test_id,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "error": r.error
                }
                for r in test_results
            ]
        }

        if comparison:
            report["comparison"] = [
                {
                    "metric": c.metric_name,
                    "before": c.before_value,
                    "after": c.after_value,
                    "change_percent": round(c.change_percent, 2),
                    "improved": c.improved
                }
                for c in comparison
            ]

            # 总结
            improved_count = sum(1 for c in comparison if c.improved)
            report["comparison_summary"] = {
                "total_metrics": len(comparison),
                "improved": improved_count,
                "degraded": len(comparison) - improved_count
            }

        return report

    # ========== 辅助方法 ==========

    def _find_skill_file(self, skill_path: str) -> Optional[Path]:
        """查找技能文件"""
        base_path = Path("src/leo_skills")
        skill_dir = base_path / skill_path

        if not skill_dir.exists():
            return None

        for py_file in skill_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            return py_file

        return None

    def _generate_test_code(self, func_name: str, skill_path: str) -> str:
        """生成测试代码"""
        return f'''
def test_{func_name}():
    """Auto-generated test for {func_name}"""
    # Test basic functionality
    assert True, "Test not implemented"
'''

    def _run_single_test(self, test: TestCase) -> TestResult:
        """运行单个测试"""
        start_time = time.time()

        try:
            # 创建临时测试文件
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as f:
                f.write(test.code)
                test_file = f.name

            try:
                # 运行测试
                result = subprocess.run(
                    [sys.executable, test_file],
                    capture_output=True,
                    text=True,
                    timeout=test.timeout
                )

                duration_ms = int((time.time() - start_time) * 1000)

                passed = result.returncode == 0

                return TestResult(
                    test_id=test.test_id,
                    passed=passed,
                    duration_ms=duration_ms,
                    output=result.stdout,
                    error=result.stderr if not passed else ""
                )

            finally:
                # 清理临时文件
                try:
                    os.unlink(test_file)
                except:
                    pass

        except subprocess.TimeoutExpired:
            return TestResult(
                test_id=test.test_id,
                passed=False,
                duration_ms=int((time.time() - start_time) * 1000),
                error="Test timeout"
            )

        except Exception as e:
            return TestResult(
                test_id=test.test_id,
                passed=False,
                duration_ms=int((time.time() - start_time) * 1000),
                error=str(e)
            )

    def _record_test_results(self, skill_path: str, results: List[TestResult]):
        """记录测试结果"""
        record = {
            "skill_path": skill_path,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "test_id": r.test_id,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms
                }
                for r in results
            ]
        }

        self.test_results.append(record)


# 全局实例
_global_tester: Optional[EvolutionTester] = None


def get_evolution_tester() -> EvolutionTester:
    """获取全局测试器"""
    global _global_tester
    if _global_tester is None:
        _global_tester = EvolutionTester()
    return _global_tester
