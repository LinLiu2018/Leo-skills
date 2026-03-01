# -*- coding: utf-8 -*-
"""
测试 Web Search Skill
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'src')

from leo_skills.utilities.web_search_skill import WebSearchSkill

def test_search():
    """测试搜索功能"""
    print("=" * 50)
    print("测试 Web Search Skill")
    print("=" * 50)

    try:
        skill = WebSearchSkill()
        print(f"[OK] Skill 初始化成功")
        print(f"  - 搜索引擎: {skill.search_engine}")
        print(f"  - Bing API: {'已配置' if skill.bing_api_key else '未配置'}")
        print(f"  - SerpAPI: {'已配置' if skill.serpapi_key else '未配置'}")

        # 测试简单搜索
        print("\n搜索: '2025年2月 AI人工智能最新新闻'...")
        result = skill.search("2025年2月 AI人工智能最新新闻", max_results=5)

        print(f"[OK] 搜索完成")
        print(f"  - 引擎: {result['engine']}")
        print(f"  - 结果数: {result['total']}")

        print("\n搜索结果:")
        for i, item in enumerate(result['results'][:5], 1):
            print(f"\n{i}. {item['title']}")
            print(f"   来源: {item['source']}")
            print(f"   摘要: {item['snippet'][:100]}...")

        return True

    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_search()
    sys.exit(0 if success else 1)
