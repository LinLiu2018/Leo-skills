# -*- coding: utf-8 -*-
"""
批量技能安全扫描脚本
扫描所有技能并生成安全评分报告
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.leo_skills.tools.skill_vetter_skill.skill_vetter_skill import SkillVetterSkill

WORKSPACE = Path(__file__).parent.parent.parent
SKILLS_DIR = WORKSPACE / "src" / "leo_skills"

print("=" * 80)
print("批量技能安全扫描")
print("=" * 80)
print()

vetter = SkillVetterSkill()
results = []

# 扫描所有技能
for category in SKILLS_DIR.iterdir():
    if not category.is_dir() or category.name.startswith('_'):
        continue
    
    for skill_dir in category.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith('_'):
            continue
        
        skill_name = skill_dir.name
        result = vetter.scan_skill(str(skill_dir))
        
        score = result.get('security_score', 0)
        level = result.get('security_level', 'Unknown')
        
        results.append({
            'name': f"{category.name}/{skill_name}",
            'score': score,
            'level': level,
            'files': result.get('files_scanned', 0)
        })
        
        # 显示低分技能
        if score < 80:
            print(f"[WARN] {category.name}/{skill_name}: {score}/100")

# 汇总统计
print()
print("=" * 80)
print("扫描汇总")
print("=" * 80)
print()

total = len(results)
safe = sum(1 for r in results if r['score'] >= 90)
warning = sum(1 for r in results if 60 <= r['score'] < 90)
danger = sum(1 for r in results if r['score'] < 60)

print(f"扫描技能总数：{total}")
print(f"[SAFE] 安全 (90-100): {safe} ({safe/total*100:.1f}%)")
print(f"[WARN] 注意 (60-89): {warning} ({warning/total*100:.1f}%)")
print(f"[DANG] 危险 (0-59): {danger} ({danger/total*100:.1f}%)")
print()

if danger > 0:
    print("[DANG] 危险技能列表:")
    for r in results:
        if r['score'] < 60:
            print(f"  - {r['name']}: {r['score']}/100")
    print()

# 保存报告
report_path = WORKSPACE / "docs" / "reference" / "skill_security_scan_20260227.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# 技能安全扫描报告\n\n")
    f.write(f"**扫描时间**: 2026-02-27\n\n")
    f.write(f"## 汇总\n\n")
    f.write(f"- 扫描技能总数：{total}\n")
    f.write(f"- [SAFE] 安全：{safe}\n")
    f.write(f"- [WARN] 注意：{warning}\n")
    f.write(f"- [DANG] 危险：{danger}\n\n")
    f.write(f"## 详细结果\n\n")
    f.write(f"| 技能 | 安全评分 | 安全等级 | 文件数 |\n")
    f.write(f"|------|----------|----------|--------|\n")
    for r in sorted(results, key=lambda x: x['score']):
        f.write(f"| {r['name']} | {r['score']} | {r['level']} | {r['files']} |\n")

print(f"报告已保存：{report_path}")
print()
print("=" * 80)
print("扫描完成")
print("=" * 80)
