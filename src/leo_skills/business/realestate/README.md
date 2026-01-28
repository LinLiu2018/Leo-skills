# 房地产业务技能目录 (Business: RealEstate)

本目录存放房地产经纪业务专用的 SKILL 模块，旨在为房产团队提供直接的业务赋能。

## 规划技能清单

| 技能名称 | 目录名 | 说明 | 优先级 |
|---------|--------|------|-------|
| 房源描述生成 | `property_desc_generator_skill` | 根据房源基础信息（面积、户型、亮点）生成多平台文案 | P0 |
| 市场周报生成 | `market_report_generator_skill` | 自动抓取并整合本地房产市场数据，生成周报 | P1 |
| 营销话术生成 | `sales_script_generator_skill` | 针对不同客户类型生成沟通话术脚本 | P2 |
| 竞对项目分析 | `competitor_analysis_skill` | 分析竞品楼盘的优劣势和定价策略 | P1 |

## 开发规范

- 所有技能必须遵循 `snake_case_skill` 命名。
- 必须包含 `SKILL.md` 和 `scripts/main.py`。
