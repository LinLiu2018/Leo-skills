# -*- coding: utf-8 -*-
"""
蓝绿部署系统

实现零停机部署
"""

import json
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class DeploymentStatus(str, Enum):
    """部署状态"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"
    ACTIVE = "active"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class Deployment:
    """部署记录"""
    deployment_id: str
    skill_path: str
    version: str
    status: DeploymentStatus
    blue_path: str = ""
    green_path: str = ""
    active_env: str = "blue"
    created_at: datetime = field(default_factory=datetime.now)
    deployed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    health_check_result: Dict = field(default_factory=dict)
    error: str = ""


class BlueGreenDeployment:
    """
    蓝绿部署

    功能：
    - 双环境切换
    - 流量控制
    - 健康检查
    - 快速回滚
    """

    def __init__(self, base_path: str = "src/leo_skills"):
        self.base_path = Path(base_path)
        self.deployments: Dict[str, Deployment] = {}
        self.deployment_history: List[Deployment] = []

    def deploy(
        self,
        skill_path: str,
        version: str,
        health_check: Optional[Callable] = None,
        verify_timeout: int = 60
    ) -> Deployment:
        """
        部署新版本

        Args:
            skill_path: 技能路径
            version: 版本号
            health_check: 健康检查函数
            verify_timeout: 验证超时时间

        Returns:
            部署记录
        """
        deployment_id = f"deploy_{skill_path.replace('/', '_')}_{int(time.time())}"

        # 确定目标环境（当前未激活的环境）
        deployment = self._get_or_create_deployment(skill_path, version)
        target_env = "green" if deployment.active_env == "blue" else "blue"
        target_path = self._get_env_path(skill_path, target_env)

        deployment.status = DeploymentStatus.DEPLOYING
        deployment.version = version
        deployment.blue_path = str(self._get_env_path(skill_path, "blue"))
        deployment.green_path = str(target_path)

        try:
            # 1. 部署到目标环境
            self._deploy_to_env(skill_path, target_env, version)

            deployment.status = DeploymentStatus.VERIFYING

            # 2. 健康检查
            if health_check:
                health_ok = self._verify_health(health_check, verify_timeout)
                deployment.health_check_result = {"passed": health_ok}

                if not health_ok:
                    deployment.status = DeploymentStatus.FAILED
                    deployment.error = "Health check failed"
                    return deployment

            # 3. 切换流量
            deployment.active_env = target_env
            deployment.status = DeploymentStatus.ACTIVE
            deployment.deployed_at = datetime.now()
            deployment.verified_at = datetime.now()

            # 4. 清理旧版本（可选）
            # self._cleanup_old_version(skill_path, target_env)

        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            deployment.error = str(e)

        # 保存部署记录
        self.deployments[skill_path] = deployment
        self.deployment_history.append(deployment)

        return deployment

    def switch_traffic(self, target_env: str) -> bool:
        """
        切换流量

        Args:
            target_env: 目标环境 (blue/green)

        Returns:
            是否成功
        """
        # 查找当前部署
        for deployment in reversed(self.deployment_history):
            if deployment.status == DeploymentStatus.ACTIVE:
                deployment.active_env = target_env
                return True

        return False

    def rollback(self, skill_path: str) -> bool:
        """
        回滚

        Args:
            skill_path: 技能路径

        Returns:
            是否成功
        """
        deployment = self.deployments.get(skill_path)
        if not deployment:
            return False

        # 切换到之前的环境
        previous_env = "green" if deployment.active_env == "blue" else "blue"
        deployment.active_env = previous_env
        deployment.status = DeploymentStatus.ROLLED_BACK

        return True

    def verify_deployment(
        self,
        skill_path: str,
        health_check: Callable,
        timeout: int = 60
    ) -> bool:
        """
        验证部署

        Args:
            skill_path: 技能路径
            health_check: 健康检查函数
            timeout: 超时时间

        Returns:
            是否验证成功
        """
        deployment = self.deployments.get(skill_path)
        if not deployment:
            return False

        return self._verify_health(health_check, timeout)

    def get_status(self, skill_path: str) -> Optional[Dict]:
        """获取部署状态"""
        deployment = self.deployments.get(skill_path)
        if not deployment:
            return None

        return {
            "skill_path": deployment.skill_path,
            "version": deployment.version,
            "status": deployment.status.value,
            "active_env": deployment.active_env,
            "blue_path": deployment.blue_path,
            "green_path": deployment.green_path,
            "deployed_at": deployment.deployed_at.isoformat() if deployment.deployed_at else None,
            "health_check": deployment.health_check_result
        }

    # ========== 辅助方法 ==========

    def _get_or_create_deployment(
        self,
        skill_path: str,
        version: str
    ) -> Deployment:
        """获取或创建部署记录"""
        deployment_id = f"deploy_{skill_path.replace('/', '_')}"

        if skill_path in self.deployments:
            return self.deployments[skill_path]

        return Deployment(
            deployment_id=deployment_id,
            skill_path=skill_path,
            version=version,
            status=DeploymentStatus.PENDING
        )

    def _get_env_path(self, skill_path: str, env: str) -> Path:
        """获取环境路径"""
        # blue 和 green 目录
        env_dir = self.base_path / f"{skill_path}.{env}"
        env_dir.mkdir(parents=True, exist_ok=True)
        return env_dir

    def _deploy_to_env(
        self,
        skill_path: str,
        env: str,
        version: str
    ):
        """部署到指定环境"""
        source_path = self.base_path / skill_path
        target_path = self._get_env_path(skill_path, env)

        if not source_path.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")

        # 复制文件
        if target_path.exists():
            shutil.rmtree(target_path)

        shutil.copytree(source_path, target_path)

        # 创建版本文件
        version_file = target_path / "VERSION"
        version_file.write_text(version)

    def _verify_health(
        self,
        health_check: Callable,
        timeout: int
    ) -> bool:
        """验证健康状态"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                if health_check():
                    return True
            except Exception as e:
                pass

            time.sleep(2)

        return False

    def _cleanup_old_version(self, skill_path: str, env: str):
        """清理旧版本"""
        # 可选实现：保留历史版本
        pass


# 全局实例
_global_deployment: Optional[BlueGreenDeployment] = None


def get_deployment() -> BlueGreenDeployment:
    """获取全局部署器"""
    global _global_deployment
    if _global_deployment is None:
        _global_deployment = BlueGreenDeployment()
    return _global_deployment
