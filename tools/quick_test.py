import sys
sys.path.insert(0, r"E:\桌面\leo_ai_system\src")

from leo_skills.development.skill_creator.skill_creator import SkillCreator

print("="*60)
print("测试 skill-creator")
print("="*60)

c = SkillCreator()

# 测试 1
print("\n[1] list_templates")
r = c.execute(action="list_templates")
print(f"    状态：{r['status']}")
print(f"    模板数：{len(r['templates'])}")

# 测试 2
print("\n[2] create")
r = c.execute(action="create", description="测试")
print(f"    状态：{r['status']}")

# 测试 3
print("\n[3] evaluate")
r = c.execute(action="evaluate", skill_path="./test")
print(f"    状态：{r['status']}")

# 测试 4
print("\n[4] benchmark")
r = c.execute(action="benchmark", skill_path="./test")
print(f"    状态：{r['status']}")

# 测试 5
print("\n[5] tune_description")
r = c.execute(action="tune_description", skill_path="./test")
print(f"    状态：{r['status']}")

# 测试 6
print("\n[6] optimize")
r = c.execute(action="optimize", skill_path="./test")
print(f"    状态：{r['status']}")

# 测试 7
print("\n[7] 错误处理")
r = c.execute(action="invalid")
print(f"    状态：{r['status']}")

print("\n" + "="*60)
print("全部测试通过!")
print("="*60)
