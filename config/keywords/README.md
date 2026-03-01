# 关键词库系统

**创建日期**: 2026-02-28  
**用途**: 统一管理所有定时任务使用的关键词，支持自动更新和进化

---

## 目录结构

```
config/keywords/
├── README.md              # 本文件
├── keyword_base.json      # 基础关键词库
├── keyword_hot.json       # 热门关键词库 (动态更新)
├── keyword_negative.json  # 负面/排除关键词库
├── keyword_history/       # 历史关键词记录
│   ├── 2026-02.json
│   └── ...
└── tools/
    ├── update_keywords.py # 关键词更新工具
    └── analyze_keywords.py # 关键词分析工具
```

---

## 关键词分类

### 1. 房产经纪
- 宁波别墅
- 度假养老
- 法拍捡漏
- 东钱湖
- ...

### 2. 商业地产
- 不良资产
- 摊位销售
- 菜场项目
- ...

### 3. AI 科技
- OpenClaw
- AI Agent
- 大模型
- ...

### 4. 跨境电商
- 智能穿戴
- 选品
- 亚马逊
- ...

---

## 关键词等级

| 等级 | 说明 | 使用策略 |
|------|------|---------|
| S 级 | 核心热词，搜索量高 | 优先使用，每日监控 |
| A 级 | 重要关键词，稳定流量 | 常规使用，每周更新 |
| B 级 | 长尾关键词，精准流量 | 补充使用，每月更新 |
| C 级 | 测试关键词，待验证 | 定期测试，优胜劣汰 |

---

## 关键词进化机制

### 自动更新
- 每日监控搜索量变化
- 自动调整关键词等级
- 淘汰低效关键词

### 手动优化
- 每周人工审核关键词库
- 添加新兴热词
- 删除过时关键词

### 效果追踪
- 记录每个关键词的点击率
- 记录转化率
- 记录内容互动数据

---

## 使用方式

### 在定时任务中调用

```python
from config.keywords import KeywordManager

km = KeywordManager()

# 获取某类别的关键词
keywords = km.get_keywords(category="房产经纪", level="S")

# 获取热门关键词
hot_keywords = km.get_hot_keywords(limit=10)

# 更新关键词效果
km.update_keyword_effect(keyword="宁波别墅", clicks=100, conversions=5)
```

---

## 维护说明

- **每日**: 自动更新热门关键词
- **每周**: 人工审核关键词库
- **每月**: 导出关键词效果报告

---

**负责人**: Leo AI System  
**下次审核**: 2026-03-07
