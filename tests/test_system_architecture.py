#!/usr/bin/env python3
"""
测试 Leo System - 日志、错误处理和性能监控
"""
import logging
import sys
import time
from pathlib import Path


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestLogger:
    """测试统一日志系统"""

    def test_get_logger_basic(self):
        """测试基本日志记录器获取"""
        from leo_system.logger import get_logger

        logger = get_logger("test_logger")

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_with_level(self):
        """测试自定义日志级别"""
        from leo_system.logger import get_logger

        logger = get_logger("test_logger_debug", level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_logger_singleton(self):
        """测试日志记录器单例行为"""
        from leo_system.logger import get_logger

        logger1 = get_logger("test_singleton")
        logger2 = get_logger("test_singleton")

        # 同名日志记录器应该是同一个实例
        assert logger1 is logger2

    def test_set_log_level(self):
        """测试设置日志级别"""
        from leo_system.logger import get_logger, set_log_level

        logger = get_logger("test_level_change")
        set_log_level(logger, logging.ERROR)

        assert logger.level == logging.ERROR

    def test_convenience_functions(self):
        """测试便捷日志函数"""
        from leo_system import logger as log_module

        # 这些函数不应该抛出异常
        log_module.debug("Debug message")
        log_module.info("Info message")
        log_module.warning("Warning message")
        log_module.error("Error message")
        log_module.critical("Critical message")


class TestErrors:
    """测试统一错误处理框架"""

    def test_leo_error_basic(self):
        """测试基础异常类"""
        from leo_system.errors import LeoError

        error = LeoError("Test error")

        assert str(error) == "[LeoError] Test error"
        assert error.message == "Test error"
        assert error.error_code == "LeoError"

    def test_leo_error_with_details(self):
        """测试带详情的异常"""
        from leo_system.errors import LeoError

        error = LeoError("Test error", error_code="TEST001", details={"key": "value", "count": 42})

        error_str = str(error)
        assert "TEST001" in error_str
        assert "Test error" in error_str
        assert "key=value" in error_str
        assert "count=42" in error_str

    def test_skill_not_found_error(self):
        """测试 Skill 未找到异常"""
        from leo_system.errors import SkillNotFoundError

        error = SkillNotFoundError("test-skill")

        assert "test-skill" in str(error)
        assert error.details["skill_name"] == "test-skill"

    def test_skill_execution_error(self):
        """测试 Skill 执行失败异常"""
        from leo_system.errors import SkillExecutionError

        error = SkillExecutionError("test-skill", "Connection timeout")

        assert "test-skill" in str(error)
        assert "Connection timeout" in str(error)
        assert error.details["skill_name"] == "test-skill"
        assert error.details["reason"] == "Connection timeout"

    def test_agent_dispatch_error(self):
        """测试 Agent 调度失败异常"""
        from leo_system.errors import AgentDispatchError

        error = AgentDispatchError("test-agent", "Agent not available")

        assert "test-agent" in str(error)
        assert "Agent not available" in str(error)

    def test_workflow_execution_error(self):
        """测试 Workflow 执行失败异常"""
        from leo_system.errors import WorkflowExecutionError

        error = WorkflowExecutionError("test-workflow", "step2", "Validation failed")

        assert "test-workflow" in str(error)
        assert "step2" in str(error)
        assert "Validation failed" in str(error)

    def test_initialization_error(self):
        """测试初始化失败异常"""
        from leo_system.errors import InitializationError

        error = InitializationError("database", "Connection refused")

        assert "database" in str(error)
        assert "Connection refused" in str(error)


class TestMetrics:
    """测试性能监控模块"""

    def test_performance_metrics_basic(self):
        """测试基本性能指标记录"""
        from leo_system.metrics import PerformanceMetrics

        metrics = PerformanceMetrics()
        metrics.record("test_operation", 1.5)

        stats = metrics.get_stats("test_operation")
        assert stats["count"] == 1
        assert stats["avg"] == 1.5
        assert stats["min"] == 1.5
        assert stats["max"] == 1.5

    def test_performance_metrics_multiple_records(self):
        """测试多次记录"""
        from leo_system.metrics import PerformanceMetrics

        metrics = PerformanceMetrics()
        metrics.record("test_op", 1.0)
        metrics.record("test_op", 2.0)
        metrics.record("test_op", 3.0)

        stats = metrics.get_stats("test_op")
        assert stats["count"] == 3
        assert stats["avg"] == 2.0
        assert stats["min"] == 1.0
        assert stats["max"] == 3.0
        assert stats["total"] == 6.0

    def test_track_time_decorator(self):
        """测试时间追踪装饰器"""
        from leo_system.metrics import get_metrics, track_time

        @track_time
        def slow_function():
            time.sleep(0.1)
            return "done"

        result = slow_function()

        assert result == "done"

        # 检查指标是否被记录
        metrics = get_metrics()
        stats = metrics.get_stats("tests.test_system_architecture.slow_function")
        assert stats["count"] >= 1

    def test_track_time_with_custom_name(self):
        """测试自定义名称的时间追踪"""
        from leo_system.metrics import get_metrics, track_time

        @track_time(name="custom_operation")
        def my_function():
            time.sleep(0.05)
            return 42

        result = my_function()

        assert result == 42

        metrics = get_metrics()
        stats = metrics.get_stats("custom_operation")
        assert stats["count"] >= 1

    def test_timer_context_manager(self):
        """测试计时器上下文管理器"""
        from leo_system.metrics import Timer, get_metrics

        with Timer("test_context", log_result=False) as timer:
            time.sleep(0.05)

        assert timer.duration is not None
        assert timer.duration >= 0.05

        metrics = get_metrics()
        stats = metrics.get_stats("test_context")
        assert stats["count"] >= 1

    def test_measure_time(self):
        """测试 measure_time 函数"""
        from leo_system.metrics import get_metrics, measure_time

        with measure_time("measured_operation"):
            time.sleep(0.05)

        metrics = get_metrics()
        stats = metrics.get_stats("measured_operation")
        assert stats["count"] >= 1
        assert stats["avg"] >= 0.05

    def test_get_performance_report(self):
        """测试性能报告生成"""
        from leo_system.metrics import get_metrics, get_performance_report

        metrics = get_metrics()
        metrics.record("op1", 1.0)
        metrics.record("op2", 2.0)

        report = get_performance_report()

        assert isinstance(report, dict)
        assert "op1" in report or "op2" in report
