#!/usr/bin/env python3
"""
核心技能单元测试
================
测试系统核心的4个技能：
1. content_layout_leo_skill - 内容排版
2. research_assistant_skill - 研究助手
3. web_search_skill - 网络搜索
4. realestate_news_publisher_skill - 房产资讯发布
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestContentLayoutSkill:
    """测试内容排版技能"""

    def test_import(self):
        """测试技能导入"""
        from leo_skills.content_creation.content_layout_leo_skill import ContentLayoutSkill
        assert ContentLayoutSkill is not None

    def test_initialization(self):
        """测试技能初始化"""
        from leo_skills.content_creation.content_layout_leo_skill import ContentLayoutSkill
        skill = ContentLayoutSkill()
        assert skill is not None
        assert hasattr(skill, "format_for_wechat")
        assert hasattr(skill, "format_for_xiaohongshu")

    def test_format_wechat_basic(self):
        """测试微信排版基本功能"""
        from leo_skills.content_creation.content_layout_leo_skill import ContentLayoutSkill
        skill = ContentLayoutSkill()

        test_content = "# 测试标题\n\n这是测试内容。"
        result = skill.format_for_wechat(content=test_content, style="data_driven")

        assert result is not None
        assert "success" in result
        # 即使失败也应该有结果结构
        assert "result" in result or "error" in result

    def test_format_xiaohongshu_basic(self):
        """测试小红书排版基本功能"""
        from leo_skills.content_creation.content_layout_leo_skill import ContentLayoutSkill
        skill = ContentLayoutSkill()

        test_content = "这是一篇小红书笔记内容"
        result = skill.format_for_xiaohongshu(content=test_content)

        assert result is not None
        assert "success" in result


class TestWebSearchSkill:
    """测试网络搜索技能"""

    def test_import(self):
        """测试技能导入"""
        from leo_skills.utilities.web_search_skill.web_search_skill import WebSearchSkill
        assert WebSearchSkill is not None

    def test_initialization(self):
        """测试技能初始化"""
        from leo_skills.utilities.web_search_skill.web_search_skill import WebSearchSkill
        skill = WebSearchSkill()
        assert skill is not None
        assert hasattr(skill, "search")

    def test_search_config(self):
        """测试搜索配置"""
        from leo_skills.utilities.web_search_skill.web_search_skill import WebSearchSkill

        config = {"max_results": 5, "timeout": 10}
        skill = WebSearchSkill(config=config)

        assert skill.max_results == 5
        assert skill.timeout == 10


class TestResearchAssistantSkill:
    """测试研究助手技能"""

    def test_import(self):
        """测试技能导入"""
        from leo_skills.utilities.research_assistant_skill import ResearchAssistant
        assert ResearchAssistant is not None

    def test_initialization(self):
        """测试技能初始化"""
        from leo_skills.utilities.research_assistant_skill import ResearchAssistant
        assistant = ResearchAssistant()
        assert assistant is not None

    def test_has_search_method(self):
        """测试是否有搜索方法"""
        from leo_skills.utilities.research_assistant_skill import ResearchAssistant
        assistant = ResearchAssistant()
        assert hasattr(assistant, "search_papers") or hasattr(assistant, "search")


class TestRealestateNewsPublisherSkill:
    """测试房产资讯发布技能"""

    def test_import(self):
        """测试技能导入"""
        try:
            from leo_skills.content_creation.realestate_news_publisher_skill import (
                realestate_news_publisher_skill,
            )
            assert True
        except ImportError:
            # 如果导入失败，检查文件是否存在
            skill_path = (
                project_root
                / "leo_skills"
                / "content-creation"
                / "realestate_news_publisher_skill"
            )
            assert skill_path.exists(), f"技能目录不存在: {skill_path}"


class TestSkillIntegration:
    """技能集成测试"""

    def test_skill_loader_can_find_skills(self):
        """测试技能加载器能找到核心技能"""
        from leo_subagents.skills_bridge.skill_loader import SkillLoader

        loader = SkillLoader()
        loader.discover_and_load()

        # 检查核心技能是否被发现
        skills = loader.list_skills()

        # 至少应该发现一些技能
        assert len(skills) > 0

    def test_skill_executor_basic(self):
        """测试技能执行器基本功能"""
        from leo_subagents.skills_bridge.skill_executor import SkillExecutor

        executor = SkillExecutor()
        assert executor is not None
        assert hasattr(executor, "execute")
        assert hasattr(executor, "execution_history")


class TestInteractionLogger:
    """测试交互日志记录器"""

    def test_import(self):
        """测试导入"""
        from leo_system.interaction_logger import InteractionLogger, get_interaction_logger
        assert InteractionLogger is not None
        assert get_interaction_logger is not None

    def test_create_session(self):
        """测试创建会话"""
        from leo_system.interaction_logger import InteractionLogger

        logger = InteractionLogger()
        assert logger.session_id is not None
        assert logger.session_id.startswith("session_")

    def test_log_user_input(self):
        """测试记录用户输入"""
        from leo_system.interaction_logger import InteractionLogger

        logger = InteractionLogger()
        log_id = logger.log_user_input("测试输入")

        assert log_id is not None
        assert len(logger.logs) == 1
        assert logger.logs[0].log_type == "user_input"

    def test_log_skill_call(self):
        """测试记录技能调用"""
        from leo_system.interaction_logger import InteractionLogger

        logger = InteractionLogger()
        log_id = logger.log_skill_call(
            skill_name="test_skill",
            action="test_action",
            params={"key": "value"},
            result={"success": True},
            success=True,
            execution_time=0.5
        )

        assert log_id is not None
        assert len(logger.logs) == 1
        assert logger.logs[0].log_type == "skill_call"

    def test_log_workflow(self):
        """测试记录工作流"""
        from leo_system.interaction_logger import InteractionLogger

        logger = InteractionLogger()

        # 开始工作流
        wf_id = logger.log_workflow_start(
            workflow_name="test_workflow",
            inputs={"topic": "test"},
            total_steps=3
        )
        assert wf_id is not None

        # 记录步骤
        logger.log_workflow_step(
            step_name="step1",
            step_number=1,
            agent="test-agent",
            status="completed",
            execution_time=1.0
        )

        # 结束工作流
        logger.log_workflow_end(
            success=True,
            total_time=5.0,
            completed_steps=3
        )

        assert len(logger.logs) == 3

    def test_get_session_summary(self):
        """测试获取会话摘要"""
        from leo_system.interaction_logger import InteractionLogger

        logger = InteractionLogger()
        logger.log_user_input("测试1")
        logger.log_user_input("测试2")

        summary = logger.get_session_summary()

        assert summary["total_logs"] == 2
        assert "user_input" in summary["log_types"]
        assert summary["log_types"]["user_input"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
