# -*- coding: utf-8 -*-
"""
关键词管理工具
用于管理、更新、分析关键词库
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class KeywordManager:
    """关键词管理器"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent
        else:
            base_path = Path(base_path)
        
        self.base_path = base_path
        self.base_file = base_path / "keyword_base.json"
        self.hot_file = base_path / "keyword_hot.json"
        self.negative_file = base_path / "keyword_negative.json"
        self.history_dir = base_path / "keyword_history"
        
        # 确保历史目录存在
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载数据
        self.base_data = self._load_json(self.base_file)
        self.hot_data = self._load_json(self.hot_file)
        self.negative_data = self._load_json(self.negative_file)
    
    def _load_json(self, file_path: Path) -> Dict:
        """加载 JSON 文件"""
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_json(self, file_path: Path, data: Dict):
        """保存 JSON 文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_keywords(self, category: str, level: str = None, limit: int = None) -> List[str]:
        """获取某类别的关键词
        
        Args:
            category: 类别名称
            level: 关键词等级 (S/A/B/C)
            limit: 返回数量限制
            
        Returns:
            关键词列表
        """
        if category not in self.base_data.get('categories', {}):
            return []
        
        keywords = self.base_data['categories'][category].get('keywords', [])
        
        # 按等级筛选
        if level:
            keywords = [kw for kw in keywords if kw.get('level') == level]
        
        # 按搜索量排序
        keywords = sorted(keywords, key=lambda x: x.get('search_volume', 0), reverse=True)
        
        # 限制数量
        if limit:
            keywords = keywords[:limit]
        
        return [kw['keyword'] for kw in keywords]
    
    def get_hot_keywords(self, category: str = None, limit: int = 10) -> List[Dict]:
        """获取热门关键词
        
        Args:
            category: 类别名称 (可选)
            limit: 返回数量限制
            
        Returns:
            热门关键词列表
        """
        hot_keywords = self.hot_data.get('hot_keywords', {})
        
        if category:
            keywords = hot_keywords.get(category, [])
        else:
            # 合并所有类别
            keywords = []
            for cat_keywords in hot_keywords.values():
                keywords.extend(cat_keywords)
        
        # 按趋势排序
        keywords = sorted(keywords, key=lambda x: x.get('trend_percent', 0), reverse=True)
        
        return keywords[:limit]
    
    def get_emerging_keywords(self, limit: int = 10) -> List[Dict]:
        """获取新兴关键词
        
        Args:
            limit: 返回数量限制
            
        Returns:
            新兴关键词列表
        """
        emerging = self.hot_data.get('emerging_keywords', [])
        return sorted(emerging, key=lambda x: x.get('growth_rate', 0), reverse=True)[:limit]
    
    def update_keyword_effect(self, keyword: str, clicks: int = 0, conversions: int = 0):
        """更新关键词效果数据
        
        Args:
            keyword: 关键词
            clicks: 点击数
            conversions: 转化数
        """
        for category, data in self.base_data.get('categories', {}).items():
            for kw in data.get('keywords', []):
                if kw['keyword'] == keyword:
                    kw['effect']['clicks'] += clicks
                    kw['effect']['conversions'] += conversions
                    if clicks > 0:
                        kw['effect']['ctr'] = conversions / clicks
                    kw['last_used'] = datetime.now().strftime('%Y-%m-%d')
                    break
        
        self._save_json(self.base_file, self.base_data)
    
    def add_keyword(self, category: str, keyword: str, level: str = 'B', 
                    search_volume: int = 1000, tags: List[str] = None):
        """添加新关键词
        
        Args:
            category: 类别
            keyword: 关键词
            level: 等级
            search_volume: 搜索量
            tags: 标签列表
        """
        if category not in self.base_data.get('categories', {}):
            self.base_data['categories'][category] = {
                'description': f'{category}相关关键词',
                'keywords': []
            }
        
        new_keyword = {
            'keyword': keyword,
            'level': level,
            'search_volume': search_volume,
            'competition': 'unknown',
            'tags': tags or [],
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'last_used': datetime.now().strftime('%Y-%m-%d'),
            'effect': {'clicks': 0, 'conversions': 0, 'ctr': 0}
        }
        
        self.base_data['categories'][category]['keywords'].append(new_keyword)
        self._save_json(self.base_file, self.base_data)
    
    def analyze_trends(self) -> Dict[str, Any]:
        """分析关键词趋势
        
        Returns:
            趋势分析结果
        """
        trends = {
            'top_growing': self.get_emerging_keywords(10),
            'hot_keywords': self.get_hot_keywords(limit=20),
            'categories': {}
        }
        
        for category, data in self.base_data.get('categories', {}).items():
            keywords = data.get('keywords', [])
            total_volume = sum(kw.get('search_volume', 0) for kw in keywords)
            avg_ctr = sum(kw.get('effect', {}).get('ctr', 0) for kw in keywords) / len(keywords) if keywords else 0
            
            trends['categories'][category] = {
                'total_keywords': len(keywords),
                'total_volume': total_volume,
                'avg_ctr': avg_ctr,
                's_level': len([kw for kw in keywords if kw.get('level') == 'S']),
                'a_level': len([kw for kw in keywords if kw.get('level') == 'A'])
            }
        
        return trends
    
    def export_monthly_report(self, year: int = None, month: int = None):
        """导出月度关键词报告
        
        Args:
            year: 年份
            month: 月份
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        report_file = self.history_dir / f"{year}-{month:02d}.json"
        
        report = {
            'period': f"{year}-{month:02d}",
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'trends': self.analyze_trends(),
            'base_data': self.base_data,
            'hot_data': self.hot_data
        }
        
        self._save_json(report_file, report)
        return report_file
    
    def save_changes(self):
        """保存所有更改"""
        self._save_json(self.base_file, self.base_data)
        self._save_json(self.hot_file, self.hot_data)
        self._save_json(self.negative_file, self.negative_data)


# 使用示例
if __name__ == "__main__":
    km = KeywordManager()
    
    # 获取房产经纪 S 级关键词
    print("房产经纪 S 级关键词:")
    for kw in km.get_keywords("房产经纪", "S", 5):
        print(f"  - {kw}")
    
    # 获取热门关键词
    print("\n热门关键词 TOP10:")
    for kw in km.get_hot_keywords(limit=10):
        print(f"  - {kw['keyword']} (趋势：+{kw['trend_percent']}%)")
    
    # 获取新兴关键词
    print("\n新兴关键词 TOP5:")
    for kw in km.get_emerging_keywords(5):
        print(f"  - {kw['keyword']} (增长率：{kw['growth_rate']}%)")
    
    # 分析趋势
    print("\n趋势分析:")
    trends = km.analyze_trends()
    for category, stats in trends['categories'].items():
        print(f"  {category}: {stats['total_keywords']} 个词，总搜索量 {stats['total_volume']}")
