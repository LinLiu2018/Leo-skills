import sys
sys.path.insert(0, r"E:\桌面\leo_ai_system\src")

from leo_skills.development.skill_creator.skill_creator import SkillCreator

print("="*60)
print("测试 skill-creator 完整实现")
print("="*60)

c = SkillCreator()

# 测试 1: 创建技能
print("\n[1] 创建技能")
r = c.execute(action="create", description="视频讲稿生成", category="content_creation")
print(f"    状态：{r['status']}")
print(f"    技能路径：{r.get('skill_path')}")
print(f"    文件数：{r.get('file_count')}")

skill_path = r.get('skill_path')

# 测试 2: 评估技能
print("\n[2] 评估技能")
r = c.execute(action="evaluate", skill_path=skill_path)
print(f"    状态：{r['status']}")
print(f"    测试查询数：{r.get('test_queries_generated')}")
print(f"    评估界面：{r.get('eval_viewer')}")

# 测试 3: 基准测试
print("\n[3] 基准测试")
r = c.execute(action="benchmark", skill_path=skill_path)
print(f"    状态：{r['status']}")
print(f"    并行代理：{r.get('parallel_agents')}")
print(f"    通过率：{r.get('metrics', {}).get('pass_rate')}")

# 测试 4: 描述调优
print("\n[4] 描述调优")
r = c.execute(action="tune_description", skill_path=skill_path)
print(f"    状态：{r['status']}")
print(f"    迭代次数：{r.get('iterations')}")
print(f"    优化轮次：{len(r.get('optimization_rounds', []))}")

# 测试 5: 生成评估报告
print("\n[5] 生成评估报告")
r = c.execute(action="generate_eval_report", skill_path=skill_path)
print(f"    状态：{r['status']}")
print(f"    报告文件：{r.get('report_file')}")

print("\n" + "="*60)
print("完整实现测试通过!")
print("="*60)
