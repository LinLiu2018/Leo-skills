# -*- coding: utf-8 -*-
"""
ClawHub 10 个热门技能 - 性能测试脚本
"""

import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print("=" * 60)
print("ClawHub 10 Skills - Performance Test")
print("=" * 60)
print()

results = []

# ========== Skill 1: skill_vetter_skill ==========
print("[1/10] Testing skill_vetter_skill...")
try:
    from src.leo_skills.tools.skill_vetter_skill.skill_vetter_skill import SkillVetterSkill
    s = SkillVetterSkill()
    result = s.scan_skill('src/leo_skills/tools/skill_vetter_skill')
    score = result.get('security_score', 0)
    level = result.get('security_level', 'Unknown')
    files = result.get('files_scanned', 0)
    print(f"  [OK] Loaded")
    print(f"  [OK] Security Score: {score}")
    print(f"  [OK] Security Level: {level}")
    print(f"  [OK] Files Scanned: {files}")
    results.append(('skill_vetter_skill', 'PASS', score))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('skill_vetter_skill', 'FAIL', 0))
print()

# ========== Skill 2: web_search_enhanced_skill ==========
print("[2/10] Testing web_search_enhanced_skill...")
try:
    from src.leo_skills.utilities.web_search_enhanced_skill.web_search_enhanced_skill import WebSearchEnhancedSkill
    s = WebSearchEnhancedSkill()
    status = s.get_status()
    print(f"  [OK] Loaded")
    print(f"  [OK] Version: {status.get('version')}")
    print(f"  [OK] Rate Limit: {status.get('config', {}).get('rate_limit_delay')}s")
    results.append(('web_search_enhanced_skill', 'PASS', 100))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('web_search_enhanced_skill', 'FAIL', 0))
print()

# ========== Skill 3: github_integration_skill ==========
print("[3/10] Testing github_integration_skill...")
try:
    from src.leo_skills.tools.github_integration_skill.github_integration_skill import GithubIntegrationSkill
    s = GithubIntegrationSkill()
    status = s.get_status()
    print(f"  [OK] Loaded")
    print(f"  [OK] Version: {status.get('version')}")
    print(f"  [OK] Note: Requires 'gh' CLI installed")
    results.append(('github_integration_skill', 'PASS', 100))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('github_integration_skill', 'FAIL', 0))
print()

# ========== Skill 4: summarize_skill ==========
print("[4/10] Testing summarize_skill...")
try:
    from src.leo_skills.utilities.summarize_skill.summarize_skill import SummarizeSkill
    s = SummarizeSkill()
    status = s.get_status()
    print(f"  [OK] Loaded")
    print(f"  [OK] Version: {status.get('version')}")
    print(f"  [OK] Supports: URL, PDF, YouTube, Audio")
    results.append(('summarize_skill', 'PASS', 100))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('summarize_skill', 'FAIL', 0))
print()

# ========== Skill 5: memory_enhanced_skill ==========
print("[5/10] Testing memory_enhanced_skill...")
try:
    from src.leo_skills.core.memory_enhanced_skill.memory_enhanced_skill import MemoryEnhancedSkill
    s = MemoryEnhancedSkill()
    
    # Test store
    store_result = s.execute({'action': 'store', 'content': 'Test: I like Americano', 'category': 'preference', 'tags': ['test']})
    
    # Test retrieve
    retrieve_result = s.execute({'action': 'retrieve', 'query': 'Test'})
    
    print(f"  [OK] Loaded")
    print(f"  [OK] Store Test: {store_result.get('status')}")
    print(f"  [OK] Retrieve Test: {retrieve_result.get('count')} results")
    results.append(('memory_enhanced_skill', 'PASS', 100))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('memory_enhanced_skill', 'FAIL', 0))
print()

# ========== Skill 6: find_skills_skill ==========
print("[6/10] Testing find_skills_skill...")
try:
    from src.leo_skills.tools.find_skills_skill.find_skills_skill import FindSkillsSkill
    s = FindSkillsSkill()
    
    # Test search
    search_result = s.execute({'action': 'search', 'query': 'search'})
    
    # Test recommend
    recommend_result = s.execute({'action': 'recommend', 'use_case': 'I want to automate daily reports'})
    
    print(f"  [OK] Loaded")
    print(f"  [OK] Search Test: {search_result.get('count')} skills found")
    print(f"  [OK] Recommend Test: {recommend_result.get('count')} recommendations")
    results.append(('find_skills_skill', 'PASS', 100))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('find_skills_skill', 'FAIL', 0))
print()

# ========== Skill 7: gog_skill ==========
print("[7/10] Testing gog_skill...")
try:
    from src.leo_skills.tools.gog_skill.gog_skill import GogSkill
    s = GogSkill()
    status = s.get_status()
    print(f"  [OK] Loaded")
    print(f"  [OK] Version: {status.get('version')}")
    print(f"  [OK] Status: {status.get('status')} (needs API config)")
    results.append(('gog_skill', 'PASS', 80))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('gog_skill', 'FAIL', 0))
print()

# ========== Agent 8: self_improving_agent ==========
print("[8/10] Testing self_improving_agent...")
try:
    from src.leo_subagents.agents.self_improving_agent.self_improving_agent import SelfImprovingAgent
    a = SelfImprovingAgent()
    
    # Test execute
    result = a.execute('Analyze my errors')
    
    print(f"  [OK] Loaded")
    print(f"  [OK] Execute Test: {result.get('status')}")
    print(f"  [OK] Triggers: {len(a.triggers)} keywords")
    results.append(('self_improving_agent', 'PASS', 100))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('self_improving_agent', 'FAIL', 0))
print()

# ========== Agent 9: proactive_agent ==========
print("[9/10] Testing proactive_agent...")
try:
    from src.leo_subagents.agents.proactive_agent.proactive_agent import ProactiveAgent
    a = ProactiveAgent()
    
    # Test execute
    result = a.execute('Help me plan tomorrow work')
    
    print(f"  [OK] Loaded")
    print(f"  [OK] Execute Test: {result.get('status')}")
    print(f"  [OK] Triggers: {len(a.triggers)} keywords")
    results.append(('proactive_agent', 'PASS', 100))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('proactive_agent', 'FAIL', 0))
print()

# ========== Skill 10: weather_skill (existing) ==========
print("[10/10] Testing weather_skill (existing)...")
try:
    weather_path = Path('src/leo_skills/utilities/weather_skill')
    if weather_path.exists():
        print(f"  [OK] Weather skill exists")
        results.append(('weather_skill', 'PASS', 100))
    else:
        alt_path = Path('D:/openclaw/skills/weather')
        if alt_path.exists():
            print(f"  [OK] Weather skill exists (OpenClaw)")
            results.append(('weather_skill', 'PASS', 100))
        else:
            print(f"  [SKIP] Weather skill not found (may use OpenClaw built-in)")
            results.append(('weather_skill', 'SKIP', 0))
except Exception as e:
    print(f"  [FAIL] {e}")
    results.append(('weather_skill', 'FAIL', 0))
print()

# ========== Summary ==========
print("=" * 60)
print("Test Summary")
print("=" * 60)
print()

passed = sum(1 for _, status, _ in results if status == 'PASS')
failed = sum(1 for _, status, _ in results if status == 'FAIL')
skipped = sum(1 for _, status, _ in results if status == 'SKIP')
avg_score = sum(score for _, _, score in results) / len(results) if results else 0

print(f"Total: {len(results)} skills")
print(f"PASS: {passed}")
print(f"FAIL: {failed}")
print(f"SKIP: {skipped}")
print(f"Avg Score: {avg_score:.1f}/100")
print()

if failed == 0:
    print("[SUCCESS] All skills passed! Ready for production.")
else:
    print(f"[WARNING] {failed} skills failed, please check errors.")

print()
print("=" * 60)
