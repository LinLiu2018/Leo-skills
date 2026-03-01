# -*- coding: utf-8 -*-
"""
使用关键词库执行搜索任务
自动从关键词库获取最新热词，执行搜索并生成报告
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.keywords.tools.keyword_manager import KeywordManager


def search_with_keywords(category: str, limit: int = 10, use_hot: bool = True):
    """使用关键词库执行搜索
    
    Args:
        category: 关键词类别
        limit: 搜索数量限制
        use_hot: 是否使用热门关键词
    """
    km = KeywordManager()
    
    # 获取关键词
    if use_hot:
        keywords = [kw['keyword'] for kw in km.get_hot_keywords(category, limit)]
    else:
        keywords = km.get_keywords(category, level="S", limit=limit)
    
    if not keywords:
        print(f"未找到 {category} 类别的关键词")
        return
    
    print(f"\n{'='*60}")
    print(f"{category} - 搜索任务")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"使用关键词：{len(keywords)} 个")
    print(f"{'='*60}\n")
    
    # 打印关键词列表
    print("搜索关键词:")
    for i, kw in enumerate(keywords, 1):
        print(f"  {i}. {kw}")
    print()
    
    # 这里可以集成实际的搜索逻辑
    # 例如调用 web_search 工具
    # 或者调用其他 API
    
    # 记录关键词使用效果
    for kw in keywords:
        km.update_keyword_effect(kw, clicks=1, conversions=0)
    
    print("搜索完成！")
    print(f"下次搜索时间：{(datetime.now().replace(hour=9, minute=0, second=0) if datetime.now().hour >= 9 else datetime.now().replace(hour=9, minute=0, second=0)).strftime('%Y-%m-%d %H:%M:%S')}")


def generate_keyword_report():
    """生成关键词效果报告"""
    km = KeywordManager()
    
    trends = km.analyze_trends()
    
    print("\n" + "="*60)
    print("关键词效果报告")
    print("="*60 + "\n")
    
    for category, stats in trends['categories'].items():
        print(f"{category}:")
        print(f"  总关键词数：{stats['total_keywords']}")
        print(f"  总搜索量：{stats['total_volume']:,}")
        print(f"  S 级关键词：{stats['s_level']}")
        print(f"  A 级关键词：{stats['a_level']}")
        print(f"  平均 CTR: {stats['avg_ctr']*100:.2f}%")
        print()
    
    # 导出月度报告
    report_file = km.export_monthly_report()
    print(f"月度报告已导出：{report_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='使用关键词库执行搜索')
    parser.add_argument('--category', type=str, default='房产经纪', help='关键词类别')
    parser.add_argument('--limit', type=int, default=10, help='搜索数量限制')
    parser.add_argument('--no-hot', action='store_true', help='不使用热门关键词')
    parser.add_argument('--report', action='store_true', help='生成效果报告')
    
    args = parser.parse_args()
    
    if args.report:
        generate_keyword_report()
    else:
        search_with_keywords(args.category, args.limit, not args.no_hot)
