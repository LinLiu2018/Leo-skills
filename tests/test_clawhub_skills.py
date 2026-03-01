# -*- coding: utf-8 -*-
"""
ClawHub 技能测试套件
目标：测试覆盖率 7% → 30%
"""

import unittest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestSkillVetterSkill(unittest.TestCase):
    """技能安全扫描器测试"""
    
    def setUp(self):
        from leo_skills.tools.skill_vetter_skill.skill_vetter_skill import SkillVetterSkill
        self.skill = SkillVetterSkill()
    
    def test_scan_existing_skill(self):
        """测试扫描现有技能"""
        result = self.skill.scan_skill('src/leo_skills/tools/skill_vetter_skill')
        self.assertIn('security_score', result)
        self.assertGreaterEqual(result['security_score'], 0)
        self.assertLessEqual(result['security_score'], 100)
    
    def test_code_generator_detection(self):
        """测试代码生成器检测"""
        is_gen = self.skill._is_code_generator('src/leo_skills/backend/flask_api_generator_skill')
        self.assertTrue(is_gen)
    
    def test_security_level(self):
        """测试安全等级判断"""
        self.assertEqual(self.skill._get_security_level(95), "[SAFE] 安全")
        self.assertEqual(self.skill._get_security_level(70), "[WARN] 注意")
        self.assertEqual(self.skill._get_security_level(40), "[DANG] 危险")


class TestWebSearchEnhancedSkill(unittest.TestCase):
    """增强版网络搜索测试"""
    
    def setUp(self):
        from leo_skills.utilities.web_search_enhanced_skill.web_search_enhanced_skill import WebSearchEnhancedSkill
        self.skill = WebSearchEnhancedSkill()
    
    def test_rate_limit(self):
        """测试速率限制"""
        self.assertGreater(self.skill.config['rate_limit_delay'], 0)
    
    def test_deduplication(self):
        """测试去重功能"""
        results = [
            {"url": "http://a.com", "title": "A"},
            {"url": "http://a.com", "title": "A Duplicate"},
            {"url": "http://b.com", "title": "B"}
        ]
        unique = self.skill._deduplicate(results)
        self.assertEqual(len(unique), 2)


class TestSummarizeSkill(unittest.TestCase):
    """内容总结技能测试"""
    
    def setUp(self):
        from leo_skills.utilities.summarize_skill.summarize_skill import SummarizeSkill
        self.skill = SummarizeSkill()
    
    def test_execute_url(self):
        """测试 URL 总结"""
        result = self.skill.execute({'type': 'url', 'url': 'http://example.com'})
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['action'], 'summarize_url')


class TestMemoryEnhancedSkill(unittest.TestCase):
    """增强记忆技能测试"""
    
    def setUp(self):
        from leo_skills.core.memory_enhanced_skill.memory_enhanced_skill import MemoryEnhancedSkill
        self.skill = MemoryEnhancedSkill()
    
    def test_store_and_retrieve(self):
        """测试存储和检索"""
        # 存储
        store_result = self.skill.execute({
            'action': 'store',
            'content': '测试记忆内容',
            'category': 'test'
        })
        self.assertEqual(store_result['status'], 'success')
        
        # 检索
        retrieve_result = self.skill.execute({
            'action': 'retrieve',
            'query': '测试'
        })
        self.assertEqual(retrieve_result['status'], 'success')
        self.assertGreater(retrieve_result['count'], 0)


class TestGithubIntegrationSkill(unittest.TestCase):
    """GitHub 集成技能测试"""
    
    def setUp(self):
        from leo_skills.tools.github_integration_skill.github_integration_skill import GithubIntegrationSkill
        self.skill = GithubIntegrationSkill()
    
    def test_status(self):
        """测试状态查询"""
        status = self.skill.get_status()
        self.assertEqual(status['name'], 'github_integration_skill')
        self.assertEqual(status['version'], '1.0.0')


class TestFindSkillsSkill(unittest.TestCase):
    """技能发现技能测试"""
    
    def setUp(self):
        from leo_skills.tools.find_skills_skill.find_skills_skill import FindSkillsSkill
        self.skill = FindSkillsSkill()
    
    def test_search(self):
        """测试技能搜索"""
        result = self.skill.execute({'action': 'search', 'query': 'search'})
        self.assertEqual(result['status'], 'success')
    
    def test_recommend(self):
        """测试技能推荐"""
        result = self.skill.execute({
            'action': 'recommend',
            'use_case': '我想自动化日报'
        })
        self.assertEqual(result['status'], 'success')


class TestSelfImprovingAgent(unittest.TestCase):
    """自我迭代 Agent 测试"""
    
    def setUp(self):
        # 直接导入，避免循环依赖
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from leo_subagents.agents.self_improving_agent.self_improving_agent import SelfImprovingAgent
        self.agent = SelfImprovingAgent()
    
    def test_execute(self):
        """测试执行"""
        result = self.agent.execute('分析我的错误')
        self.assertEqual(result['status'], 'success')
    
    def test_triggers(self):
        """测试触发词"""
        self.assertIn('自我优化', self.agent.triggers)
        self.assertGreater(len(self.agent.triggers), 0)


class TestProactiveAgent(unittest.TestCase):
    """主动规划 Agent 测试"""
    
    def setUp(self):
        # 直接导入，避免循环依赖
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from leo_subagents.agents.proactive_agent.proactive_agent import ProactiveAgent
        self.agent = ProactiveAgent()
    
    def test_plan_task(self):
        """测试任务规划"""
        result = self.agent.execute('帮我规划明天的工作')
        self.assertEqual(result['status'], 'success')


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_cron_schedule_distribution(self):
        """测试 Cron 时间分散"""
        import json
        from pathlib import Path
        import os
        
        # 使用环境变量或默认路径
        home_dir = os.path.expanduser('~')
        jobs_file = Path(home_dir) / ".openclaw" / "cron" / "jobs.json"
        
        # 如果文件不存在，跳过测试
        if not jobs_file.exists():
            self.skipTest("Cron jobs file not found")
            return
        
        with open(jobs_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jobs = data.get('jobs', [])
        eight_am_count = sum(1 for j in jobs if j.get('schedule', {}).get('expr', '').startswith('0 8 '))
        
        # 8:00 时段不应超过 5 个任务
        self.assertLessEqual(eight_am_count, 5, "8:00 时段任务过多，应分散执行")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
