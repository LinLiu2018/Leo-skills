# -*- coding: utf-8 -*-
"""
fission_miniprogram_skill - 裂变小程序技能

提供裂变营销小程序的设计、开发和管理功能，包括分享机制、激励机制和数据分析。
"""
from leo_skills.core.base_executor import BaseExecutor

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum


class FissionType(Enum):
    """裂变类型"""
    INVITE = "invite"          # 邀请裂变
    SHARE = "share"            # 分享裂变
    GROUP_BUY = "group_buy"    # 拼团裂变
    HELPER = "helper"          # 助力裂变
    REDEEM = "redeem"          # 兑换裂变


class RewardType(Enum):
    """奖励类型"""
    COUPON = "coupon"
    CASH = "cash"
    CREDIT = "credit"
    PRODUCT = "product"
    DISCOUNT = "discount"


@dataclass
class FissionRule:
    """裂变规则"""
    fission_type: str
    required_invites: int
    reward_type: str
    reward_value: float
    max_rewards: int = -1  # -1表示无限
    expiration_days: int = 7


@dataclass
class FissionParticipant:
    """裂变参与者"""
    user_id: str
    invite_code: str
    invited_count: int = 0
    rewards: List[Dict] = field(default_factory=list)
    joined_at: str = ""


class FissionMiniprogramSkill(BaseExecutor):
    """
    裂变小程序技能

    功能：
    - 裂变活动配置
    - 邀请码生成
    - 奖励机制管理
    - 裂变数据统计
    - 分享链路追踪
    - 活动效果分析

    使用场景：
    - 裂变营销活动
    - 用户增长策略
    - 社交电商运营
    - 品牌传播活动
    """

    def __init__(self):
        self.name = "fission_miniprogram_skill"
        self.version = "1.0.0"
        self.description = "裂变小程序技能 - 提供裂变营销功能"

        # 存储裂变活动
        self.activities: Dict[str, Dict] = {}
        self.participants: Dict[str, FissionParticipant] = {}

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行裂变操作

        Args:
            action: 操作类型
                - create_activity: 创建裂变活动
                - generate_code: 生成邀请码
                - record_invite: 记录邀请
                - claim_reward: 领取奖励
                - get_activity: 获取活动信息
                - get_stats: 获取统计数据
                - end_activity: 结束活动
            activity_id: 活动ID
            user_id: 用户ID
            rule_config: 规则配置

        Returns:
            Dict 包含执行结果
        """
        action = kwargs.get("action", "create_activity")

        try:
            if action == "create_activity":
                return self._create_activity(kwargs)
            elif action == "generate_code":
                return self._generate_code(kwargs)
            elif action == "record_invite":
                return self._record_invite(kwargs)
            elif action == "claim_reward":
                return self._claim_reward(kwargs)
            elif action == "get_activity":
                return self._get_activity(kwargs.get("activity_id", ""))
            elif action == "get_stats":
                return self._get_stats(kwargs)
            elif action == "end_activity":
                return self._end_activity(kwargs.get("activity_id", ""))
            elif action == "list_activities":
                return self._list_activities()
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}

        except Exception as e:
            return {"status": "error", "error": str(e), "skill": self.name}

    def _create_activity(self, kwargs: Dict) -> Dict[str, Any]:
        """创建裂变活动"""
        name = kwargs.get("name", "")
        fission_type = kwargs.get("fission_type", "invite")
        required_invites = kwargs.get("required_invites", 3)
        reward_type = kwargs.get("reward_type", "coupon")
        reward_value = kwargs.get("reward_value", 10)
        max_rewards = kwargs.get("max_rewards", -1)
        expiration_days = kwargs.get("expiration_days", 7)

        if not name:
            return {"status": "error", "message": "Activity name is required"}

        # 生成活动ID
        activity_id = f"fission_{uuid.uuid4().hex[:8]}"

        activity = {
            "id": activity_id,
            "name": name,
            "type": fission_type,
            "rule": {
                "required_invites": required_invites,
                "reward_type": reward_type,
                "reward_value": reward_value,
                "max_rewards": max_rewards,
                "expiration_days": expiration_days
            },
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=expiration_days)).isoformat(),
            "stats": {
                "total_participants": 0,
                "total_invites": 0,
                "total_rewards": 0
            }
        }

        self.activities[activity_id] = activity

        return {
            "status": "success",
            "skill": self.name,
            "activity": {
                "id": activity_id,
                "name": name,
                "type": fission_type,
                "rule": activity["rule"]
            }
        }

    def _generate_code(self, kwargs: Dict) -> Dict[str, Any]:
        """生成邀请码"""
        activity_id = kwargs.get("activity_id", "")
        user_id = kwargs.get("user_id", "")

        if not activity_id or activity_id not in self.activities:
            return {"status": "error", "message": "Invalid activity ID"}

        if not user_id:
            return {"status": "error", "message": "User ID is required"}

        # 检查是否已有邀请码
        if user_id in self.participants:
            return {
                "status": "success",
                "skill": self.name,
                "invite_code": self.participants[user_id].invite_code,
                "existing": True
            }

        # 生成邀请码
        invite_code = f"{activity_id[:8]}_{uuid.uuid4().hex[:6]}".upper()

        # 创建参与者
        participant = FissionParticipant(
            user_id=user_id,
            invite_code=invite_code,
            joined_at=datetime.now().isoformat()
        )

        self.participants[user_id] = participant

        # 更新活动统计
        self.activities[activity_id]["stats"]["total_participants"] += 1

        return {
            "status": "success",
            "skill": self.name,
            "invite_code": invite_code,
            "share_url": f"https://miniprogram.com/fission/{invite_code}",
            "existing": False
        }

    def _record_invite(self, kwargs: Dict) -> Dict[str, Any]:
        """记录邀请"""
        activity_id = kwargs.get("activity_id", "")
        inviter_id = kwargs.get("inviter_id", "")
        invitee_id = kwargs.get("invitee_id", "")

        if not all([activity_id, inviter_id, invitee_id]):
            return {"status": "error", "message": "Missing required parameters"}

        # 检查活动
        if activity_id not in self.activities:
            return {"status": "error", "message": "Invalid activity ID"}

        # 检查被邀请者是否已参与
        if invitee_id in self.participants:
            return {"status": "error", "message": "Invitee already participated"}

        # 为被邀请者生成邀请码
        invite_code = f"{activity_id[:8]}_{uuid.uuid4().hex[:6]}".upper()
        participant = FissionParticipant(
            user_id=invitee_id,
            invite_code=invite_code,
            joined_at=datetime.now().isoformat()
        )
        self.participants[invitee_id] = participant

        # 更新邀请者计数
        if inviter_id in self.participants:
            self.participants[inviter_id].invited_count += 1

        # 更新活动统计
        self.activities[activity_id]["stats"]["total_invites"] += 1

        # 检查是否达到奖励条件
        rule = self.activities[activity_id]["rule"]
        current_count = self.participants[inviter_id].invited_count

        reward_ready = current_count >= rule["required_invites"]

        return {
            "status": "success",
            "skill": self.name,
            "inviter_id": inviter_id,
            "invitee_id": invitee_id,
            "invited_count": current_count,
            "required_invites": rule["required_invites"],
            "reward_ready": reward_ready
        }

    def _claim_reward(self, kwargs: Dict) -> Dict[str, Any]:
        """领取奖励"""
        activity_id = kwargs.get("activity_id", "")
        user_id = kwargs.get("user_id", "")

        if not all([activity_id, user_id]):
            return {"status": "error", "message": "Missing required parameters"}

        if activity_id not in self.activities:
            return {"status": "error", "message": "Invalid activity ID"}

        if user_id not in self.participants:
            return {"status": "error", "message": "User not in activity"}

        activity = self.activities[activity_id]
        participant = self.participants[user_id]
        rule = activity["rule"]

        # 检查是否达到条件
        if participant.invited_count < rule["required_invites"]:
            return {
                "status": "error",
                "message": f"Not enough invites. Need {rule['required_invites'] - participant.invited_count} more"
            }

        # 检查是否已领取过
        for reward in participant.rewards:
            if reward.get("activity_id") == activity_id:
                return {"status": "error", "message": "Reward already claimed"}

        # 发放奖励
        reward = {
            "activity_id": activity_id,
            "type": rule["reward_type"],
            "value": rule["reward_value"],
            "claimed_at": datetime.now().isoformat()
        }

        participant.rewards.append(reward)
        activity["stats"]["total_rewards"] += 1

        # 生成奖励信息
        reward_info = self._format_reward(rule["reward_type"], rule["reward_value"])

        return {
            "status": "success",
            "skill": self.name,
            "reward": reward_info,
            "user_id": user_id,
            "total_invites": participant.invited_count
        }

    def _format_reward(self, reward_type: str, value: float) -> str:
        """格式化奖励信息"""
        formats = {
            "coupon": f"{value}元优惠券",
            "cash": f"{value}元现金",
            "credit": f"{value}积分",
            "product": "指定商品",
            "discount": f"{int(value * 10)}折优惠"
        }
        return formats.get(reward_type, f"{value}")

    def _get_activity(self, activity_id: str) -> Dict[str, Any]:
        """获取活动信息"""
        if not activity_id or activity_id not in self.activities:
            return {"status": "error", "message": "Invalid activity ID"}

        activity = self.activities[activity_id]
        return {
            "status": "success",
            "skill": self.name,
            "activity": {
                "id": activity_id,
                "name": activity["name"],
                "type": activity["type"],
                "status": activity["status"],
                "rule": activity["rule"],
                "expires_at": activity["expires_at"],
                "stats": activity["stats"]
            }
        }

    def _get_stats(self, kwargs: Dict) -> Dict[str, Any]:
        """获取统计数据"""
        activity_id = kwargs.get("activity_id", "")

        if activity_id and activity_id in self.activities:
            activity = self.activities[activity_id]
            stats = activity["stats"]
            return {
                "status": "success",
                "skill": self.name,
                "activity_id": activity_id,
                "stats": {
                    "total_participants": stats["total_participants"],
                    "total_invites": stats["total_invites"],
                    "total_rewards": stats["total_rewards"],
                    "conversion_rate": round(
                        stats["total_rewards"] / stats["total_participants"] * 100, 2
                    ) if stats["total_participants"] > 0 else 0
                }
            }

        # 汇总所有活动
        total_stats = {
            "total_participants": 0,
            "total_invites": 0,
            "total_rewards": 0,
            "active_activities": 0
        }

        for activity in self.activities.values():
            if activity["status"] == "active":
                total_stats["active_activities"] += 1
            for key in total_stats:
                if key != "active_activities":
                    total_stats[key] += activity["stats"].get(key, 0)

        return {
            "status": "success",
            "skill": self.name,
            "stats": total_stats
        }

    def _end_activity(self, activity_id: str) -> Dict[str, Any]:
        """结束活动"""
        if not activity_id or activity_id not in self.activities:
            return {"status": "error", "message": "Invalid activity ID"}

        self.activities[activity_id]["status"] = "ended"
        self.activities[activity_id]["ended_at"] = datetime.now().isoformat()

        return {
            "status": "success",
            "skill": self.name,
            "activity_id": activity_id,
            "message": "Activity ended successfully",
            "final_stats": self.activities[activity_id]["stats"]
        }

    def _list_activities(self) -> Dict[str, Any]:
        """列出所有活动"""
        activities = []
        for activity_id, activity in self.activities.items():
            activities.append({
                "id": activity_id,
                "name": activity["name"],
                "type": activity["type"],
                "status": activity["status"],
                "participants": activity["stats"]["total_participants"]
            })

        return {
            "status": "success",
            "skill": self.name,
            "activities": activities,
            "total": len(activities)
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "activity_creation",
                "invite_code_generation",
                "invite_tracking",
                "reward_management",
                "statistics_tracking",
                "activity_lifecycle"
            ],
            "fission_types": [t.value for t in FissionType],
            "reward_types": [t.value for t in RewardType]
        }


# 向后兼容
Fission_Miniprogram_Skill = FissionMiniprogramSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Fission Miniprogram Skill - 演示")
    print("=" * 60)

    skill = FissionMiniprogramSkill()

    # 演示1: 创建裂变活动
    print("\n1. 创建裂变活动")
    print("-" * 40)
    result = skill.execute(
        action="create_activity",
        name="邀请好友得优惠券",
        fission_type="invite",
        required_invites=3,
        reward_type="coupon",
        reward_value=10,
        expiration_days=14
    )
    activity_id = result["activity"]["id"]
    print(f"活动ID: {activity_id}")
    print(f"活动名称: {result['activity']['name']}")

    # 演示2: 生成邀请码
    print("\n2. 生成邀请码")
    print("-" * 40)
    result = skill.execute(
        action="generate_code",
        activity_id=activity_id,
        user_id="user_001"
    )
    print(f"邀请码: {result['invite_code']}")
    print(f"分享链接: {result['share_url']}")

    # 演示3: 记录邀请
    print("\n3. 记录邀请")
    print("-" * 40)
    result = skill.execute(
        action="record_invite",
        activity_id=activity_id,
        inviter_id="user_001",
        invitee_id="user_002"
    )
    print(f"邀请者: {result['inviter_id']}")
    print(f"已邀请: {result['invited_count']}/{result['required_invites']}")

    # 继续邀请以达到奖励条件
    skill.execute(
        action="record_invite",
        activity_id=activity_id,
        inviter_id="user_001",
        invitee_id="user_003"
    )
    skill.execute(
        action="record_invite",
        activity_id=activity_id,
        inviter_id="user_001",
        invitee_id="user_004"
    )

    # 演示4: 领取奖励
    print("\n4. 领取奖励")
    print("-" * 40)
    result = skill.execute(
        action="claim_reward",
        activity_id=activity_id,
        user_id="user_001"
    )
    print(f"奖励: {result['reward']}")
    print(f"总邀请: {result['total_invites']}")

    # 演示5: 获取统计
    print("\n5. 获取统计")
    print("-" * 40)
    result = skill.execute(action="get_stats", activity_id=activity_id)
    print(f"总参与: {result['stats']['total_participants']}")
    print(f"总邀请: {result['stats']['total_invites']}")
    print(f"转化率: {result['stats']['conversion_rate']}%")

    # 演示6: 列出活动
    print("\n6. 列出所有活动")
    print("-" * 40)
    result = skill.execute(action="list_activities")
    print(f"活动总数: {result['total']}")
    for a in result['activities']:
        print(f"  - {a['name']} ({a['status']})")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
