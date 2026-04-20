#!/usr/bin/env python3
"""
批量评估所有剩余 Leo Skills - 后台运行版
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r"E:\桌面\leo_ai_system\src")

from leo_skills.development.skill_creator.skill_creator import SkillCreator

SKILLS_DIR = Path(r"E:\桌面\leo_ai_system\src\leo_skills")

def batch_assess_all():
    """批量评估所有技能"""
    
    print("="*60)
    print("批量评估所有 Leo Skills")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    creator = SkillCreator()
    skill_dirs = [d for d in SKILLS_DIR.rglob("*_skill") if d.is_dir()]
    
    # 跳过前 20 个已评估的
    skill_dirs = skill_dirs[20:]
    
    print(f"剩余技能数：{len(skill_dirs)}")
    print(f"预计耗时：{len(skill_dirs) * 30 / 60:.0f} 分钟")
    
    results = []
    start_time = time.time()
    
    for i, skill_dir in enumerate(skill_dirs, 1):
        skill_name = skill_dir.name
        skill_path = str(skill_dir)
        category = skill_dir.parent.name
        
        # 进度
        elapsed = time.time() - start_time
        eta = (elapsed / i) * (len(skill_dirs) - i) / 60
        
        print(f"\n[{i}/{len(skill_dirs)}] {category}/{skill_name} (剩余：{eta:.0f}分钟)")
        
        try:
            # 1. 评估
            r1 = creator.execute(action="evaluate", skill_path=skill_path)
            status1 = "OK" if r1["status"] == "success" else "ERR"
            
            # 2. 基准测试
            r2 = creator.execute(action="benchmark", skill_path=skill_path)
            status2 = "OK" if r2["status"] == "success" else "ERR"
            
            # 3. 描述调优
            r3 = creator.execute(action="tune_description", skill_path=skill_path)
            status3 = "OK" if r3["status"] == "success" else "ERR"
            
            # 4. 生成报告
            r4 = creator.execute(action="generate_eval_report", skill_path=skill_path)
            status4 = "OK" if r4["status"] == "success" else "ERR"
            
            all_ok = all(s == "OK" for s in [status1, status2, status3, status4])
            status = "[OK]" if all_ok else "[PARTIAL]"
            
            print(f"  {status} 评估:{r1.get('test_queries_generated',0)} 基准:{r2.get('metrics',{}).get('pass_rate',0)*100:.0f}% 调优:{r3.get('iterations',0)}轮")
            
            results.append({
                "name": skill_name,
                "category": category,
                "path": skill_path,
                "status": "success" if all_ok else "partial",
                "assessed_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"  [ERR] {e}")
            results.append({
                "name": skill_name,
                "category": category,
                "path": skill_path,
                "status": "error",
                "error": str(e)
            })
        
        # 每 50 个保存一次进度
        if i % 50 == 0:
            save_progress(results, i, len(skill_dirs))
            print(f"  [SAVE] 进度已保存")
    
    # 最终保存
    save_progress(results, len(skill_dirs), len(skill_dirs))
    
    # 总结
    elapsed = (time.time() - start_time) / 60
    success = len([r for r in results if r["status"] == "success"])
    partial = len([r for r in results if r["status"] == "partial"])
    errors = len([r for r in results if r["status"] == "error"])
    
    print("\n" + "="*60)
    print("批量评估完成！")
    print("="*60)
    print(f"总耗时：{elapsed:.1f} 分钟")
    print(f"成功：{success} | 部分成功：{partial} | 错误：{errors}")
    print(f"成功率：{success/len(results)*100:.1f}%")
    print(f"报告：E:\\桌面\\leo_ai_system\\src\\docs\\batch_all_results.json")
    print("="*60)

def save_progress(results, current, total):
    """保存进度"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "progress": f"{current}/{total}",
        "completed": current,
        "total": total,
        "results": results
    }
    
    report_file = Path(r"E:\桌面\leo_ai_system\src\docs\batch_all_results.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    batch_assess_all()
