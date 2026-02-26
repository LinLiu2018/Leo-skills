#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Leo System Health Monitor

系统健康监控和性能检查工具，基于业界最佳实践实现全面的系统监控。
"""

import os
import sys
import json
import time
import psutil
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from leo_subagents.skills_bridge.skill_discovery_simple import SkillDiscoverySystem

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('health_monitor.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

@dataclass
class HealthMetrics:
    """健康检查指标"""
    timestamp: str
    system: Dict[str, Any]
    skills: Dict[str, Any]
    performance: Dict[str, Any]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    overall_score: float  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

@dataclass
class SystemMetrics:
    """系统指标"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    disk_free_gb: float
    python_version: str
    platform: str
    uptime_hours: float

@dataclass
class PerformanceMetrics:
    """性能指标"""
    skill_discovery_time: float
    validation_time: float
    registry_load_time: float
    total_skills: int
    valid_skills: int
    invalid_skills: int

class HealthMonitor:
    """健康监控系统"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.discovery = SkillDiscoverySystem(project_root)
        self.health_log_dir = project_root / ".claude" / "health"
        self.health_log_dir.mkdir(exist_ok=True)
        
        # 性能基准
        self.performance_thresholds = {
            'skill_discovery_time': 30.0,  # 秒
            'validation_time': 5.0,         # 秒
            'registry_load_time': 2.0,       # 秒
            'max_cpu_percent': 80.0,         # 百分比
            'max_memory_percent': 85.0,       # 百分比
            'max_disk_usage': 90.0,          # 百分比
            'min_valid_skill_ratio': 0.6     # 60%的技能应该有效
        }
    
    def get_system_metrics(self) -> SystemMetrics:
        """获取系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 磁盘使用率
        disk = psutil.disk_usage(str(self.project_root))
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024**3)
        
        # 系统信息
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        platform = sys.platform
        
        # 系统启动时间
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_hours = uptime_seconds / 3600
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage_percent=disk_usage_percent,
            disk_free_gb=disk_free_gb,
            python_version=python_version,
            platform=platform,
            uptime_hours=uptime_hours
        )
    
    async def measure_performance(self) -> PerformanceMetrics:
        """测量性能指标"""
        times = {}
        
        # 测量技能发现时间
        start_time = time.time()
        discovered_skills = self.discovery.discover_skills()
        times['skill_discovery'] = time.time() - start_time
        
        # 测量验证时间
        start_time = time.time()
        validation_results = []
        for skill_key, skill_data in discovered_skills.items():
            skill_path = Path(skill_data['path'])
            is_valid, errors = self.discovery._validate_skill(skill_path)
            validation_results.append((skill_key, is_valid, errors))
        times['validation'] = time.time() - start_time
        
        # 测量注册表加载时间
        start_time = time.time()
        registry = self.discovery._load_registry()
        times['registry_load'] = time.time() - start_time
        
        # 统计技能信息
        total_skills = len(discovered_skills)
        valid_skills = sum(1 for _, is_valid, _ in validation_results if is_valid)
        invalid_skills = total_skills - valid_skills
        
        return PerformanceMetrics(
            skill_discovery_time=times['skill_discovery'],
            validation_time=times['validation'],
            registry_load_time=times['registry_load'],
            total_skills=total_skills,
            valid_skills=valid_skills,
            invalid_skills=invalid_skills
        )
    
    def check_system_health(self, metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """检查系统健康状况"""
        issues = []
        thresholds = self.performance_thresholds
        
        # CPU检查
        if metrics.cpu_percent > thresholds['max_cpu_percent']:
            issues.append({
                'type': 'system',
                'severity': 'warning',
                'category': 'performance',
                'message': f"CPU使用率过高: {metrics.cpu_percent:.1f}%",
                'threshold': thresholds['max_cpu_percent'],
                'current_value': metrics.cpu_percent
            })
        
        # 内存检查
        if metrics.memory_percent > thresholds['max_memory_percent']:
            issues.append({
                'type': 'system',
                'severity': 'warning',
                'category': 'performance',
                'message': f"内存使用率过高: {metrics.memory_percent:.1f}%",
                'threshold': thresholds['max_memory_percent'],
                'current_value': metrics.memory_percent
            })
        
        # 磁盘检查
        if metrics.disk_usage_percent > thresholds['max_disk_usage']:
            issues.append({
                'type': 'system',
                'severity': 'critical',
                'category': 'storage',
                'message': f"磁盘使用率过高: {metrics.disk_usage_percent:.1f}%",
                'threshold': thresholds['max_disk_usage'],
                'current_value': metrics.disk_usage_percent
            })
        
        # 磁盘空间检查
        if metrics.disk_free_gb < 1.0:
            issues.append({
                'type': 'system',
                'severity': 'critical',
                'category': 'storage',
                'message': f"磁盘空间不足: {metrics.disk_free_gb:.1f}GB",
                'threshold': 1.0,
                'current_value': metrics.disk_free_gb
            })
        
        return issues
    
    def check_performance_health(self, perf_metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """检查性能健康状况"""
        issues = []
        thresholds = self.performance_thresholds
        
        # 技能发现时间检查
        if perf_metrics.skill_discovery_time > thresholds['skill_discovery_time']:
            issues.append({
                'type': 'performance',
                'severity': 'warning',
                'category': 'speed',
                'message': f"技能发现时间过长: {perf_metrics.skill_discovery_time:.2f}秒",
                'threshold': thresholds['skill_discovery_time'],
                'current_value': perf_metrics.skill_discovery_time
            })
        
        # 验证时间检查
        if perf_metrics.validation_time > thresholds['validation_time']:
            issues.append({
                'type': 'performance',
                'severity': 'warning',
                'category': 'speed',
                'message': f"技能验证时间过长: {perf_metrics.validation_time:.2f}秒",
                'threshold': thresholds['validation_time'],
                'current_value': perf_metrics.validation_time
            })
        
        # 有效技能比例检查
        if perf_metrics.total_skills > 0:
            valid_ratio = perf_metrics.valid_skills / perf_metrics.total_skills
            if valid_ratio < thresholds['min_valid_skill_ratio']:
                issues.append({
                    'type': 'quality',
                    'severity': 'warning',
                    'category': 'skills',
                    'message': f"有效技能比例过低: {valid_ratio:.1%}",
                    'threshold': thresholds['min_valid_skill_ratio'],
                    'current_value': valid_ratio
                })
        
        return issues
    
    def generate_recommendations(self, issues: List[Dict[str, Any]], 
                              system_metrics: SystemMetrics,
                              perf_metrics: PerformanceMetrics) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for issue in issues:
            category = issue.get('category', '')
            severity = issue.get('severity', '')
            
            if category == 'performance':
                if 'CPU使用率' in issue['message']:
                    recommendations.append("考虑关闭不必要的程序或优化代码以降低CPU使用率")
                elif '内存使用率' in issue['message']:
                    recommendations.append("考虑增加内存或优化内存使用，清理不必要的进程")
                elif '时间过长' in issue['message']:
                    recommendations.append("考虑优化技能发现算法或减少技能数量")
            
            elif category == 'storage':
                if '磁盘使用率' in issue['message']:
                    recommendations.append("清理不必要的文件，考虑扩展存储空间")
                elif '磁盘空间不足' in issue['message']:
                    recommendations.append("立即清理磁盘空间，删除临时文件和日志")
            
            elif category == 'skills':
                if '有效技能比例' in issue['message']:
                    recommendations.append("检查和修复无效技能，确保技能结构完整")
        
        # 通用建议
        if perf_metrics.invalid_skills > 0:
            recommendations.append(f"修复{perf_metrics.invalid_skills}个无效技能以提高系统质量")
        
        if system_metrics.uptime_hours > 24 * 7:  # 超过一周
            recommendations.append("系统运行时间较长，建议重启以清理内存")
        
        # 性能优化建议
        if perf_metrics.skill_discovery_time > 10:
            recommendations.append("考虑实现技能缓存机制以提高发现速度")
        
        return list(set(recommendations))  # 去重
    
    def calculate_overall_score(self, issues: List[Dict[str, Any]], 
                              perf_metrics: PerformanceMetrics) -> float:
        """计算总体健康分数 (0-100)"""
        base_score = 100.0
        
        # 根据问题扣分
        for issue in issues:
            severity = issue.get('severity', 'warning')
            if severity == 'critical':
                base_score -= 20
            elif severity == 'warning':
                base_score -= 10
            else:
                base_score -= 5
        
        # 根据性能扣分
        if perf_metrics.skill_discovery_time > self.performance_thresholds['skill_discovery_time']:
            base_score -= 10
        
        if perf_metrics.total_skills > 0:
            valid_ratio = perf_metrics.valid_skills / perf_metrics.total_skills
            if valid_ratio < self.performance_thresholds['min_valid_skill_ratio']:
                base_score -= 15
        
        return max(0.0, min(100.0, base_score))
    
    async def run_health_check(self) -> HealthMetrics:
        """运行完整的健康检查"""
        safe_print("开始系统健康检查...")
        
        # 获取系统指标
        system_metrics = self.get_system_metrics()
        
        # 测量性能
        perf_metrics = await self.measure_performance()
        
        # 更新注册表以获取最新技能状态
        status = self.discovery.get_status_report()
        
        # 检查健康问题
        system_issues = self.check_system_health(system_metrics)
        perf_issues = self.check_performance_health(perf_metrics)
        all_issues = system_issues + perf_issues
        
        # 生成建议
        recommendations = self.generate_recommendations(all_issues, system_metrics, perf_metrics)
        
        # 计算总体分数
        overall_score = self.calculate_overall_score(all_issues, perf_metrics)
        
        # 创建健康指标
        health_metrics = HealthMetrics(
            timestamp=datetime.now().isoformat(),
            system=asdict(system_metrics),
            skills=status,
            performance=asdict(perf_metrics),
            issues=all_issues,
            recommendations=recommendations,
            overall_score=overall_score
        )
        
        # 保存健康检查结果
        await self.save_health_report(health_metrics)
        
        return health_metrics
    
    async def save_health_report(self, metrics: HealthMetrics):
        """保存健康检查报告"""
        # 保存到JSON文件
        report_file = self.health_log_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(metrics.to_dict(), f, indent=2, ensure_ascii=False)
        
        # 保存最新的健康状态
        latest_file = self.health_log_dir / "latest_health.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(metrics.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"健康检查报告已保存: {report_file}")
    
    def display_health_report(self, metrics: HealthMetrics):
        """显示健康检查报告"""
        safe_print(f"\n{'='*60}")
        safe_print(f"Leo AI System Health Report")
        safe_print(f"{'='*60}")
        
        # 总体分数
        score_color = "🟢" if metrics.overall_score >= 80 else "🟡" if metrics.overall_score >= 60 else "🔴"
        safe_print(f"\n📊 总体健康分数: {metrics.overall_score:.1f}/100 {score_color}")
        
        # 系统指标
        sys_metrics = metrics.system
        safe_print(f"\n🖥️  系统指标:")
        safe_print(f"  CPU使用率: {sys_metrics['cpu_percent']:.1f}%")
        safe_print(f"  内存使用率: {sys_metrics['memory_percent']:.1f}%")
        safe_print(f"  磁盘使用率: {sys_metrics['disk_usage_percent']:.1f}%")
        safe_print(f"  可用磁盘空间: {sys_metrics['disk_free_gb']:.1f}GB")
        safe_print(f"  Python版本: {sys_metrics['python_version']}")
        safe_print(f"  运行时间: {sys_metrics['uptime_hours']:.1f}小时")
        
        # 技能指标
        skill_metrics = metrics.skills
        safe_print(f"\n🧩 技能指标:")
        safe_print(f"  总技能数: {skill_metrics['total_skills']}")
        safe_print(f"  有效技能: {skill_metrics['valid_skills']}")
        safe_print(f"  无效技能: {skill_metrics['invalid_skills']}")
        safe_print(f"  分类数: {skill_metrics['categories']}")
        
        # 性能指标
        perf_metrics = metrics.performance
        safe_print(f"\n⚡ 性能指标:")
        safe_print(f"  技能发现时间: {perf_metrics['skill_discovery_time']:.2f}秒")
        safe_print(f"  验证时间: {perf_metrics['validation_time']:.2f}秒")
        safe_print(f"  注册表加载时间: {perf_metrics['registry_load_time']:.2f}秒")
        
        # 健康问题
        if metrics.issues:
            safe_print(f"\n⚠️  发现的问题 ({len(metrics.issues)}个):")
            for i, issue in enumerate(metrics.issues, 1):
                severity_icon = "🔴" if issue['severity'] == 'critical' else "🟡"
                safe_print(f"  {i}. {severity_icon} {issue['message']}")
        else:
            safe_print(f"\n✅ 未发现健康问题")
        
        # 优化建议
        if metrics.recommendations:
            safe_print(f"\n💡 优化建议 ({len(metrics.recommendations)}条):")
            for i, rec in enumerate(metrics.recommendations, 1):
                safe_print(f"  {i}. {rec}")
        
        safe_print(f"\n📅 检查时间: {metrics.timestamp}")
        safe_print(f"{'='*60}")
    
    async def start_monitoring(self, interval_minutes: int = 60):
        """启动持续监控"""
        safe_print(f"启动持续监控，检查间隔: {interval_minutes}分钟")
        
        while True:
            try:
                metrics = await self.run_health_check()
                self.display_health_report(metrics)
                
                # 如果分数过低，发送警报
                if metrics.overall_score < 60:
                    safe_print("🚨 健康分数过低，请立即检查系统！")
                
                # 等待下次检查
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                safe_print("监控已停止")
                break
            except Exception as e:
                logger.error(f"监控过程中出错: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再重试

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Leo System Health Monitor')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in minutes')
    parser.add_argument('--output-json', type=str, help='Output health report to JSON file')
    
    args = parser.parse_args()
    
    # 创建健康监控器
    monitor = HealthMonitor(Path(args.project_root))
    
    if args.monitor:
        # 启动持续监控
        await monitor.start_monitoring(args.interval)
    else:
        # 运行单次检查
        metrics = await monitor.run_health_check()
        monitor.display_health_report(metrics)
        
        # 保存到指定文件
        if args.output_json:
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(metrics.to_dict(), f, indent=2, ensure_ascii=False)
            safe_print(f"\n健康报告已保存到: {args.output_json}")

if __name__ == "__main__":
    asyncio.run(main())