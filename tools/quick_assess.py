import sys
sys.path.insert(0, r"E:\桌面\leo_ai_system\src")

from leo_skills.development.skill_creator.skill_creator import SkillCreator
from pathlib import Path

print("="*60)
print("评估核心技能")
print("="*60)

c = SkillCreator()

skills_dir = Path(r"E:\桌面\leo_ai_system\src\leo_skills")

# 核心技能列表
core_skills = [
    ("skill-code-generator", skills_dir / "development" / "skill_code_generator_skill"),
    ("agent-skill-creator", skills_dir / "tools" / "agent_skill_creator_skill"),
]

print("\n[1] 评估技能")
print("-"*60)

for name, path in core_skills:
    r = c.execute(action="evaluate", skill_path=str(path))
    status = "[OK]" if r['status'] == 'success' else "[ERR]"
    print(f"  {status} {name}: {r['status']}")

print("\n[2] 基准测试")
print("-"*60)

for name, path in core_skills:
    r = c.execute(action="benchmark", skill_path=str(path))
    status = "[OK]" if r['status'] == 'success' else "[ERR]"
    print(f"  {status} {name}: {r['status']} (并行代理：{r.get('parallel_agents', 0)})")

print("\n[3] 描述调优")
print("-"*60)

# 测试描述调优
for name, path in core_skills:
    r = c.execute(action="tune_description", skill_path=str(path))
    status = "[OK]" if r['status'] == 'success' else "[ERR]"
    print(f"  {status} {name}: {r['status']} (迭代：{r.get('iterations', 0)})")

print("\n" + "="*60)
print("评估完成！")
print("="*60)
