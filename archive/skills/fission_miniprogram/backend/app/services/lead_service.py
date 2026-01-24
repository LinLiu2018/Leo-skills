"""
Lead Service
"""
from typing import List, Optional
from app import db
from app.models.lead import Lead


class LeadService:
    """
    Lead业务逻辑层
    """

    @staticmethod
    def create(data: dict) -> Lead:
        """创建Lead"""
        item = Lead(**data)
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def get_by_id(item_id: int) -> Optional[Lead]:
        """根据ID获取"""
        return Lead.query.get(item_id)

    @staticmethod
    def get_all(page: int = 1, per_page: int = 20) -> List[Lead]:
        """获取列表（分页）"""
        return Lead.query.paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def update(item_id: int, data: dict) -> Optional[Lead]:
        """更新"""
        item = Lead.query.get(item_id)
        if not item:
            return None
        for key, value in data.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        db.session.commit()
        return item

    @staticmethod
    def delete(item_id: int) -> bool:
        """删除"""
        item = Lead.query.get(item_id)
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

    @staticmethod
    def filter_by(**kwargs) -> List[Lead]:
        """条件查询"""
        return Lead.query.filter_by(**kwargs).all()
