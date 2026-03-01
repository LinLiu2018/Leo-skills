# Leo AI System - 依赖安装指南

## 快速安装

在终端中运行以下命令：

```bash
# 1. 安装 pip (如果未安装)
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
py -3 get-pip.py

# 2. 安装 pyyaml
py -3 -m pip install pyyaml

# 3. 测试
cd D:/桌面/leo_ai_system/src
py -3 ../scripts/quick_run.py list
```

## 手动下载安装

如果 pip 安装失败，可以手动下载 wheel 文件：

1. 访问 https://pyyaml.org/download/pyyaml/
2. 下载 `PyYAML-{version}-cp314-cp314-win_amd64.whl`
3. 运行：`py -3 -m pip install PyYAML-{version}-cp314-cp314-win_amd64.whl`

## 当前系统状态

| 组件 | 状态 |
|------|------|
| Python 3 | ✅ 已安装 |
| pip | ❌ 未安装 |
| pyyaml | ❌ 未安装 |
| Leo System 脚本 | ✅ 已就绪 |

## 安装后测试

```bash
# 列出所有能力
py -3 ../scripts/quick_run.py list

# 调用技能
py -3 ../scripts/quick_run.py skill web_search_skill '{}'

# 调用代理
py -3 ../scripts/quick_run.py agent research_agent "调研AI最新动态"

# 运行工作流
py -3 ../scripts/quick_run.py workflow research_pipeline '{}'
```

## 常见问题

**Q: 提示 "python: No module named pip"**
A: 需要先运行 get-pip.py 安装 pip

**Q: 提示 "ModuleNotFoundError: No module named 'yaml'"**
A: 这是因为 pyyaml 未安装，安装后即可解决

**Q: 脚本路径问题**
A: 确保从 `D:/桌面/leo_ai_system/src` 目录运行脚本
