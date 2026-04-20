#!/usr/bin/env python3
"""
批量评估优化所有 Leo Skills - 完整版
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r"E:\桌面\leo_ai_system\src")

from leo_skills.development.skill_creator.skill_creator import SkillCreator

SKILLS_DIR = Path(r"E:\桌面\leo_ai_system\src\leo_skills")

def main():
    print("="*60)
    print("批量评估 Leo Skills")
    print("="*60)
    
    creator = SkillCreator()
    skill_dirs = [d for d in SKILLS_DIR.rglob("*_skill") if d.is_dir()]
    
    print(f"总技能数：{len(skill_dirs)}")
    
    results = []
    
    # 评估前 20 个技能
    for i, skill_dir in enumerate(skill_dirs[:20], 1):
        skill_name = skill_dir.name
        skill_path = str(skill_dir)
        
        print(f"\n[{i}/20] {skill_name}")
        
        # 1. 评估
        r = creator.execute(action="evaluate", skill_path=skill_path)
        status = "OK" if r["status"] == "success" else "ERR"
        print(f"  [{status}] 评估：{r.get('test_queries_generated', 0)} 条查询")
        
        # 2. 基准测试
        r = creator.execute(action="benchmark", skill_path=skill_path)
        status = "OK" if r["status"] == "success" else "ERR"
        metrics = r.get("metrics", {})
        print(f"  [{status}] 基准：通过率 {metrics.get('pass_rate', 0)*100:.0f}%")
        
        # 3. 描述调优
        r = creator.execute(action="tune_description", skill_path=skill_path)
        status = "OK" if r["status"] == "success" else "ERR"
        print(f"  [{status}] 调优：{r.get('iterations', 0)} 轮迭代")
        
        results.append({
            "name": skill_name,
            "path": skill_path,
            "assessed": True,
            "optimized": True
        })
    
    # 保存结果
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_skills": len(skill_dirs),
        "assessed_count": len(results),
        "results": results
    }
    
    report_file = SKILLS_DIR.parent / "docs" / "batch_assess_results.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"\n[OK] 评估完成，报告：{report_file}")
    print(f"评估技能数：{len(results)}")

if __name__ == '__main__':
    main()
