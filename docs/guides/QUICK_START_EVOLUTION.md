# 技能自我进化 - 快速开始指南

## 🚀 5分钟快速上手

### 1. 验证框架安装

```bash
cd leo_skills
python test_evolution.py
```

应该看到：

```
✓ 所有基础测试通过！
```

### 2. 创建你的第一个可进化技能

```python
# my_skill.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.evolution import EvolvableSkill

class MySkill(EvolvableSkill):
    def __init__(self):
        super().__init__(
            skill_name="my-skill",
            config_path="config.yaml"
        )

    def _execute_core(self, text="", **kwargs):
        # 你的业务逻辑
        result = text.upper()

        return {
            'success': True,
            'result': result,
            'quality_score': min(len(result) / 100, 1.0),
            'output_metrics': {
                'length': len(result)
            }
        }

# 使用技能
if __name__ == "__main__":
    skill = MySkill()

    # 执行多次以收集数据
    for i in range(15):
        result = skill.execute(text=f"test {i}")
        print(f"[{i+1}] Success: {result.success}, Quality: {result.data.get('quality_score', 0):.2f}")

    # 查看进化状态
    status = skill.get_evolution_status()
    print(f"\n总执行次数: {status['total_executions']}")
    print(f"最佳实践数: {status['best_practices_count']}")

    # 手动触发学习
    skill.trigger_manual_learning()
```

### 3. 创建配置文件

```yaml
# config.yaml
skill_name: "my-skill"
version: "1.0.0"

evolution:
  enabled: true
  learning:
    min_executions_for_learning: 10
  optimization:
    auto_optimize: false
```

### 4. 运行并观察

```bash
python my_skill.py
```

### 5. 查看学习结果

```bash
# 查看执行历史
cat leo_skills/.evolution_data/my-skill/execution_history.jsonl

# 查看最佳实践
cat leo_skills/.evolution_data/my-skill/best_practices.json

# 查看优化规则
cat leo_skills/.evolution_data/my-skill/optimization_rules.json
```

## 📚 更多资源

- **完整文档**：`leo_skills/core/evolution/README.md`
- **配置模板**：`leo_skills/core/evolution/config/evolution_config_template.yaml`
- **实施报告**：`SKILL_EVOLUTION_IMPLEMENTATION_REPORT.md`

## 🎯 改造现有技能

### 步骤1：继承EvolvableSkill

```python
# 原代码
class MyExistingSkill:
    def run(self):
        # 原有逻辑
        pass

# 改造后
from core.evolution import EvolvableSkill

class MyExistingSkill(EvolvableSkill):
    def __init__(self):
        super().__init__(
            skill_name="my-existing-skill",
            config_path="config/config.yaml"
        )

    def _execute_core(self, **kwargs):
        # 调用原有逻辑
        result = self.original_logic(**kwargs)

        # 返回标准格式
        return {
            'success': True,
            'result': result,
            'quality_score': self._calculate_quality(result)
        }
```

### 步骤2：添加进化配置

```bash
cp leo_skills/core/evolution/config/evolution_config_template.yaml \
   your-skill/config/evolution_config.yaml
```

### 步骤3：测试运行

```python
skill = MyExistingSkill()
result = skill.execute(param1="value1")
print(skill.get_evolution_status())
```

## ✅ 完成

你的技能现在具备了自我进化能力！

每次执行都会：

1. 自动收集数据
2. 达到阈值后自动分析
3. 提取最佳实践
4. 生成优化建议

享受技能的持续进化吧！🎉
