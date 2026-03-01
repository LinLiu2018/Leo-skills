# -*- coding: utf-8 -*-
"""
口袋助理CRM集成技能 - 核心模块
对接口袋助理CRM，AI增强客户管理
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

SKILL_DIR = Path(__file__).parent.resolve()


@dataclass
class Customer:
    """客户数据模型"""
    name: str
    phone: str = ""
    stage: str = "获客"
    tags: List[str] = field(default_factory=list)
    source: str = ""
    last_contact: Optional[str] = None
    notes: str = ""
    assigned_to: str = ""


@dataclass
class FollowupRecord:
    """跟进记录"""
    customer_name: str
    date: str
    method: str  # 电话/微信/面谈
    content: str
    next_action: str = ""


class PocketCRM:
    """口袋助理CRM集成引擎"""

    def __init__(self, api_key: str = "", config: Optional[Dict[str, Any]] = None):
        self.api_key = api_key
        self.config = config or {}
        self._customers: List[Customer] = []
        self._records: List[FollowupRecord] = []
        logger.info("PocketCRM 初始化完成")

    def get_customers(
        self,
        stage: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Customer]:
        """获取客户列表，支持按阶段和标签筛选"""
        result = self._customers
        if stage:
            result = [c for c in result if c.stage == stage]
        if tags:
            result = [
                c for c in result
                if any(t in c.tags for t in tags)
            ]
        return result

    def add_customer(self, customer: Customer) -> None:
        """添加客户"""
        self._customers.append(customer)
        logger.info(f"添加客户: {customer.name}")

    def update_stage(self, name: str, new_stage: str) -> bool:
        """更新客户阶段"""
        for c in self._customers:
            if c.name == name:
                old_stage = c.stage
                c.stage = new_stage
                logger.info(f"客户 {name}: {old_stage} → {new_stage}")
                return True
        return False

    def add_followup_record(self, record: FollowupRecord) -> None:
        """添加跟进记录"""
        self._records.append(record)

    def analyze_followup_status(self) -> Dict[str, Any]:
        """分析所有客户的跟进状态"""
        today = datetime.now()
        overdue = []
        normal = []
        no_contact = []

        for c in self._customers:
            if not c.last_contact:
                no_contact.append(c.name)
                continue
            try:
                last = datetime.strptime(c.last_contact, "%Y-%m-%d")
                gap = (today - last).days
            except ValueError:
                no_contact.append(c.name)
                continue

            if gap > 7:
                overdue.append({"name": c.name, "days": gap, "stage": c.stage})
            else:
                normal.append({"name": c.name, "days": gap, "stage": c.stage})

        return {
            "total": len(self._customers),
            "overdue": overdue,
            "normal": normal,
            "no_contact": no_contact,
            "overdue_count": len(overdue),
        }

    def generate_daily_report(self) -> Dict[str, Any]:
        """生成销售日报"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_records = [
            r for r in self._records if r.date == today_str
        ]

        stage_counts = {}
        for c in self._customers:
            stage_counts[c.stage] = stage_counts.get(c.stage, 0) + 1

        return {
            "date": today_str,
            "total_customers": len(self._customers),
            "today_followups": len(today_records),
            "stage_distribution": stage_counts,
            "followup_details": [
                {
                    "customer": r.customer_name,
                    "method": r.method,
                    "content": r.content[:50],
                }
                for r in today_records
            ],
        }

    def import_from_csv(self, filepath: str) -> int:
        """从CSV文件导入客户数据"""
        import csv
        count = 0
        path = Path(filepath)
        if not path.exists():
            logger.error(f"文件不存在: {filepath}")
            return 0

        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer = Customer(
                    name=row.get("姓名", row.get("name", "")),
                    phone=row.get("电话", row.get("phone", "")),
                    stage=row.get("阶段", row.get("stage", "获客")),
                    tags=row.get("标签", row.get("tags", "")).split(","),
                    source=row.get("来源", row.get("source", "")),
                    last_contact=row.get("最后联系", row.get("last_contact", "")),
                )
                if customer.name:
                    self.add_customer(customer)
                    count += 1

        logger.info(f"从 {filepath} 导入 {count} 条客户数据")
        return count

    def export_to_json(self, filepath: str) -> None:
        """导出客户数据为JSON"""
        from dataclasses import asdict
        data = [asdict(c) for c in self._customers]
        Path(filepath).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(f"导出 {len(data)} 条客户数据到 {filepath}")
