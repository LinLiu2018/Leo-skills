"""
Leo Core 模块测试
================
测试 leo_core 模块的核心功能。
"""

import pytest
from datetime import datetime

# 测试类型定义
from leo_core.types import (
    Status,
    BaseRequest,
    BaseResponse,
    AgentCapabilities,
    SkillDefinition,
    MemoryEntry,
    Event,
    LLMConfig,
)


class TestTypes:
    """类型定义测试"""

    def test_base_request(self):
        """测试 BaseRequest"""
        request = BaseRequest(
            input="测试输入",
            context={"key": "value"},
            parameters={"depth": "detailed"}
        )
        assert request.input == "测试输入"
        assert request.context == {"key": "value"}
        assert request.parameters == {"depth": "detailed"}

    def test_base_request_defaults(self):
        """测试 BaseRequest 默认值"""
        request = BaseRequest(input="测试")
        assert request.context == {}
        assert request.parameters == {}
        assert request.session_id is None

    def test_base_response(self):
        """测试 BaseResponse"""
        response = BaseResponse(
            output="测试输出",
            status=Status.SUCCESS,
            metadata={"key": "value"}
        )
        assert response.output == "测试输出"
        assert response.status == Status.SUCCESS
        assert response.metadata == {"key": "value"}

    def test_base_response_to_dict(self):
        """测试 BaseResponse 序列化"""
        response = BaseResponse(
            output="测试输出",
            status=Status.SUCCESS
        )
        data = response.to_dict()
        assert data["output"] == "测试输出"
        assert data["status"] == "success"
        assert "timestamp" in data

    def test_agent_capabilities(self):
        """测试 AgentCapabilities"""
        capabilities = AgentCapabilities(
            name="test_agent",
            description="测试 Agent",
            version="1.0.0",
            tags=["test", "demo"],
            supported_intents=["intent1", "intent2"]
        )
        assert capabilities.name == "test_agent"
        assert capabilities.version == "1.0.0"

        data = capabilities.to_dict()
        assert data["name"] == "test_agent"

    def test_skill_definition(self):
        """测试 SkillDefinition"""
        skill = SkillDefinition(
            name="test_skill",
            description="测试 Skill",
            category="test",
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        assert skill.name == "test_skill"
        assert skill.category == "test"

    def test_memory_entry(self):
        """测试 MemoryEntry"""
        entry = MemoryEntry(
            id="mem_1",
            content="测试记忆内容",
            type="general",
            tags=["tag1", "tag2"],
            user_id="user_1"
        )
        assert entry.id == "mem_1"
        assert entry.content == "测试记忆内容"
        assert "tag1" in entry.tags
        assert entry.created_at is not None

    def test_event(self):
        """测试 Event"""
        event = Event(
            type="test.event",
            payload={"key": "value"},
            source="test_source"
        )
        assert event.type == "test.event"
        assert event.payload == {"key": "value"}
        assert event.source == "test_source"
        assert event.id is not None

    def test_llm_config(self):
        """测试 LLMConfig"""
        config = LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key="test_key",
            temperature=0.5
        )
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.temperature == 0.5


# 测试异常
from leo_core.exceptions import (
    ErrorCode,
    LeoException,
    AgentNotFoundException,
    SkillExecutionException,
    format_error_response,
    is_retryable_error,
)


class TestExceptions:
    """异常测试"""

    def test_leo_exception(self):
        """测试基础异常"""
        exc = LeoException(
            message="测试错误",
            code=ErrorCode.INVALID_INPUT,
            details={"key": "value"}
        )
        assert exc.message == "测试错误"
        assert exc.code == ErrorCode.INVALID_INPUT
        assert exc.details["key"] == "value"

    def test_leo_exception_to_dict(self):
        """测试异常序列化"""
        exc = LeoException(
            message="测试错误",
            code=ErrorCode.AGENT_NOT_FOUND,
            details={"agent_name": "test"}
        )
        data = exc.to_dict()
        assert data["error"]["code"] == ErrorCode.AGENT_NOT_FOUND.value
        assert data["error"]["message"] == "测试错误"

    def test_agent_not_found_exception(self):
        """测试 Agent 未找到异常"""
        exc = AgentNotFoundException("test_agent")
        assert "test_agent" in str(exc)
        assert exc.code == ErrorCode.AGENT_NOT_FOUND

    def test_skill_execution_exception(self):
        """测试 Skill 执行异常"""
        exc = SkillExecutionException("test_skill", "执行失败")
        assert "test_skill" in str(exc)
        assert exc.code == ErrorCode.SKILL_EXECUTION_FAILED

    def test_format_error_response(self):
        """测试错误响应格式化"""
        # 测试 LeoException
        exc = LeoException("测试", ErrorCode.INVALID_INPUT)
        result = format_error_response(exc)
        assert "error" in result
        assert result["error"]["code"] == ErrorCode.INVALID_INPUT.value

        # 测试未知异常
        result = format_error_response(ValueError("未知错误"))
        assert result["error"]["code"] == ErrorCode.UNKNOWN_ERROR.value

    def test_is_retryable_error(self):
        """测试可重试错误判断"""
        # 可重试错误
        from leo_core.exceptions import LLMTimeoutException, LLMRateLimitException
        assert is_retryable_error(LLMTimeoutException("gpt-4", 30))
        assert is_retryable_error(LLMRateLimitException("gpt-4"))

        # 不可重试错误
        assert not is_retryable_error(AgentNotFoundException("test"))
        assert not is_retryable_error(ValueError("error"))


# 测试日志
from leo_core.logging import (
    get_logger,
    LogManager,
    LogConfig,
    setup_logging,
)


class TestLogging:
    """日志测试"""

    def test_get_logger(self):
        """测试获取日志器"""
        logger = get_logger("test")
        assert logger.name == "test"

    def test_log_manager_singleton(self):
        """测试 LogManager 单例"""
        manager1 = LogManager()
        manager2 = LogManager()
        assert manager1 is manager2


# 测试事件
from leo_core.events import (
    EventBus,
    Event,
    subscribe,
    publish_event,
    get_event_bus,
)


@pytest.mark.asyncio
class TestEvents:
    """事件测试"""

    async def test_event_bus_publish_subscribe(self):
        """测试事件发布订阅"""
        received = []

        async def handler(event):
            received.append(event)

        bus = EventBus()
        bus.subscribe(handler, event_types={"test.event"})

        event = Event(
            type="test.event",
            payload={"data": "test"},
            source="test"
        )
        await bus.publish(event)

        assert len(received) == 1
        assert received[0].type == "test.event"

    async def test_publish_event_helper(self):
        """测试便捷发布函数"""
        received = []

        async def handler(event):
            received.append(event)

        bus = get_event_bus()
        bus.subscribe(handler)

        await publish_event("test.event", {"key": "value"}, "test_source")

        assert len(received) == 1
        assert received[0].payload["key"] == "value"


# 测试 MCP 工具
from leo_gateway.mcp import (
    ToolCategory,
    ToolDefinition,
    ToolRegistry,
    get_tool_registry,
)


class TestMCPTools:
    """MCP 工具测试"""

    def test_tool_registry(self):
        """测试工具注册表"""
        registry = ToolRegistry()

        async def test_handler(**kwargs):
            return {"result": "success"}

        tool_def = ToolDefinition(
            name="test_tool",
            description="测试工具",
            category=ToolCategory.SYSTEM,
            input_schema={"type": "object"}
        )
        registry.register(tool_def, test_handler)

        assert registry.exists("test_tool")
        assert registry.get("test_tool").name == "test_tool"
        assert registry.get_handler("test_tool") is not None

    def test_tool_registry_list(self):
        """测试工具列表"""
        registry = ToolRegistry()

        async def handler1(**kwargs):
            pass

        async def handler2(**kwargs):
            pass

        registry.register(
            ToolDefinition("tool1", "desc1", ToolCategory.AGENT),
            handler1
        )
        registry.register(
            ToolDefinition("tool2", "desc2", ToolCategory.SKILL),
            handler2
        )

        all_tools = registry.list_all()
        assert len(all_tools) == 2

        agent_tools = registry.list_by_category(ToolCategory.AGENT)
        assert len(agent_tools) == 1


# 测试 MCP 资源
from leo_gateway.mcp import (
    ResourceType,
    ResourceDefinition,
    ResourceRegistry,
    get_resource_registry,
    CacheStrategy,
)


class TestMCPResources:
    """MCP 资源测试"""

    def test_resource_registry(self):
        """测试资源注册表"""
        registry = ResourceRegistry()

        async def test_reader():
            return '{"data": "test"}'

        resource_def = ResourceDefinition(
            uri="leo://test/resource",
            name="Test Resource",
            description="测试资源",
            resource_type=ResourceType.CONFIG
        )
        registry.register(resource_def, test_reader)

        assert registry.exists("leo://test/resource")
        assert registry.get("leo://test/resource").name == "Test Resource"

    def test_cache_strategy(self):
        """测试缓存策略"""
        strategy = CacheStrategy(ttl=600, cache=True)
        assert strategy.ttl == 600
        assert strategy.cache is True


# 测试 MCP 监控
from leo_gateway.mcp import (
    RequestStatus,
    MCPMonitor,
    RateLimiter,
    RateLimitConfig,
)


class TestMCPMonitoring:
    """MCP 监控测试"""

    def test_mcp_monitor(self):
        """测试 MCP 监控器"""
        monitor = MCPMonitor()

        # 开始请求
        request = monitor.start_request(
            tool_name="test_tool",
            input_data={"key": "value"}
        )

        # 结束请求
        monitor.end_request(
            request=request,
            status=RequestStatus.SUCCESS,
            output_data={"result": "success"}
        )

        stats = monitor.get_stats()
        assert stats["total_requests"] == 1

    def test_mcp_monitor_stats_by_tool(self):
        """测试按工具统计"""
        monitor = MCPMonitor()

        # 多个请求
        req1 = monitor.start_request("tool_a")
        monitor.end_request(req1, RequestStatus.SUCCESS)

        req2 = monitor.start_request("tool_a")
        monitor.end_request(req2, RequestStatus.ERROR)

        req3 = monitor.start_request("tool_b")
        monitor.end_request(req3, RequestStatus.SUCCESS)

        stats = monitor.get_stats("tool_a")
        assert stats["total"] == 2
        assert stats["success"] == 1
        assert stats["error"] == 1


@pytest.mark.asyncio
class TestRateLimiter:
    """速率限制器测试"""

    async def test_rate_limiter(self):
        """测试速率限制"""
        config = RateLimitConfig(max_requests=3, window_seconds=60)
        limiter = RateLimiter(config)

        # 前3个请求应该通过
        assert await limiter.check("client_1") is True
        assert await limiter.check("client_1") is True
        assert await limiter.check("client_1") is True

        # 第4个请求应该被拒绝
        assert await limiter.check("client_1") is False

    async def test_rate_limiter_different_clients(self):
        """测试不同客户端"""
        config = RateLimitConfig(max_requests=2, window_seconds=60)
        limiter = RateLimiter(config)

        # 客户端1
        assert await limiter.check("client_1") is True
        assert await limiter.check("client_1") is False

        # 客户端2 独立计数
        assert await limiter.check("client_2") is True
        assert await limiter.check("client_2") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
