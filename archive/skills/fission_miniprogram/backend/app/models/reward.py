"""
Reward Model
"""
from datetime import datetime
from app import db


class Reward(db.Model):
    """
    Reward数据模型
    """
    __tablename__ = 'rewards'

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, nullable=False)
    reward_type = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'reward_type': self.reward_type,
            'amount': self.amount,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Reward {self.id}>'
