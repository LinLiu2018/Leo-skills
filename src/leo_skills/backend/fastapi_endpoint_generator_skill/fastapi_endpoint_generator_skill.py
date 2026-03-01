"""
fastapi_endpoint_generator_skill - FastAPI 端点生成技能

自动生成 FastAPI 路由、Pydantic Schema 和 CRUD 操作代码。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class FastAPIEndpointGenerator(BaseExecutor):
    """FastAPI 端点生成器 - 生成路由、Schema 和 CRUD 代码"""

    def __init__(self, output_dir: str = ".") -> None:
        self.name = "fastapi_endpoint_generator_skill"
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------
    # BaseExecutor 入口
    # ------------------------------------------------------------------

    def execute(
        self,
        action: str = "generate",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """执行技能

        支持的 action:
            generate - 生成 FastAPI 端点代码（默认）

        参数（通过 context 或 kwargs 传入）:
            resource_name: str          - 资源名称（必填）
            endpoints: List[Dict]       - 端点列表（可选，默认生成标准 CRUD）
            pydantic_models: List[Dict] - Pydantic 模型列表（可选）
            output_dir: str             - 输出目录（可选）
        """
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        if "output_dir" in params:
            self.output_dir = Path(params["output_dir"])

        if action == "generate":
            return self._action_generate(params)

        return {"status": "error", "message": f"未知的 action: {action}"}

    # ------------------------------------------------------------------
    # action: generate
    # ------------------------------------------------------------------

    def _action_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成 FastAPI 端点代码"""
        resource_name: str = params.get("resource_name", "")
        endpoints: Optional[List[Dict]] = params.get("endpoints")
        pydantic_models: Optional[List[Dict]] = params.get("pydantic_models")

        if not resource_name:
            return {"status": "error", "message": "resource_name 参数不能为空"}

        # 默认生成标准 CRUD 端点
        if endpoints is None:
            endpoints = [
                {"method": "GET", "path": "/", "description": "获取列表"},
                {"method": "GET", "path": "/{id}", "description": "获取详情"},
                {"method": "POST", "path": "/", "description": "创建"},
                {"method": "PUT", "path": "/{id}", "description": "更新"},
                {"method": "DELETE", "path": "/{id}", "description": "删除"},
            ]

        result = {
            "router": self._generate_router(resource_name, endpoints),
            "schemas": self._generate_schemas(resource_name, pydantic_models),
            "crud": self._generate_crud(resource_name),
        }

        return {"status": "success", "action": "generate", "data": result}

    # ------------------------------------------------------------------
    # 路由生成
    # ------------------------------------------------------------------

    def _generate_router(self, name: str, endpoints: List[Dict]) -> str:
        """生成 FastAPI 路由代码"""
        pascal = self._to_pascal(name)

        endpoint_code: List[str] = []
        for ep in endpoints:
            method = ep.get("method", "GET").lower()
            path = ep.get("path", "/")
            desc = ep.get("description", "")

            if method == "get" and "{id}" not in path:
                endpoint_code.append(f'''
@router.get("/", response_model=List[{pascal}Response])
async def list_{name}s(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """{desc}"""
    return crud.get_{name}s(db, skip=skip, limit=limit)
''')
            elif method == "get":
                endpoint_code.append(f'''
@router.get("/{{id}}", response_model={pascal}Response)
async def get_{name}(id: int, db: Session = Depends(get_db)):
    """{desc}"""
    db_item = crud.get_{name}(db, id=id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="{pascal} not found")
    return db_item
''')
            elif method == "post":
                endpoint_code.append(f'''
@router.post("/", response_model={pascal}Response, status_code=201)
async def create_{name}(
    item: {pascal}Create,
    db: Session = Depends(get_db)
):
    """{desc}"""
    return crud.create_{name}(db, item=item)
''')
            elif method == "put":
                endpoint_code.append(f'''
@router.put("/{{id}}", response_model={pascal}Response)
async def update_{name}(
    id: int,
    item: {pascal}Update,
    db: Session = Depends(get_db)
):
    """{desc}"""
    db_item = crud.update_{name}(db, id=id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="{pascal} not found")
    return db_item
''')
            elif method == "delete":
                endpoint_code.append(f'''
@router.delete("/{{id}}")
async def delete_{name}(id: int, db: Session = Depends(get_db)):
    """{desc}"""
    success = crud.delete_{name}(db, id=id)
    if not success:
        raise HTTPException(status_code=404, detail="{pascal} not found")
    return {{"message": "Deleted successfully"}}
''')

        endpoints_str = "\n".join(endpoint_code)

        return f'''"""
{pascal} API Router
Generated by Leo FastAPI Endpoint Generator
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.{name} import {pascal}Create, {pascal}Update, {pascal}Response
from app.crud import {name} as crud

router = APIRouter(prefix="/{name}s", tags=["{pascal}s"])
{endpoints_str}
'''

    # ------------------------------------------------------------------
    # Pydantic Schema 生成
    # ------------------------------------------------------------------

    def _generate_schemas(
        self, name: str, models: Optional[List[Dict]] = None
    ) -> str:
        """生成 Pydantic Schema 代码"""
        pascal = self._to_pascal(name)

        return f'''"""
{pascal} Pydantic Schemas
Generated by Leo FastAPI Endpoint Generator
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class {pascal}Base(BaseModel):
    """基础模型"""
    name: str
    description: Optional[str] = None


class {pascal}Create({pascal}Base):
    """创建模型"""
    pass


class {pascal}Update(BaseModel):
    """更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None


class {pascal}Response({pascal}Base):
    """响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
'''

    # ------------------------------------------------------------------
    # CRUD 操作生成
    # ------------------------------------------------------------------

    def _generate_crud(self, name: str) -> str:
        """生成 CRUD 操作代码"""
        pascal = self._to_pascal(name)

        return f'''"""
{pascal} CRUD Operations
Generated by Leo FastAPI Endpoint Generator
"""

from sqlalchemy.orm import Session
from app.models.{name} import {pascal}
from app.schemas.{name} import {pascal}Create, {pascal}Update


def get_{name}(db: Session, id: int):
    """获取单个记录"""
    return db.query({pascal}).filter({pascal}.id == id).first()


def get_{name}s(db: Session, skip: int = 0, limit: int = 100):
    """获取列表"""
    return db.query({pascal}).offset(skip).limit(limit).all()


def create_{name}(db: Session, item: {pascal}Create):
    """创建记录"""
    db_item = {pascal}(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_{name}(db: Session, id: int, item: {pascal}Update):
    """更新记录"""
    db_item = get_{name}(db, id)
    if db_item:
        update_data = item.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item


def delete_{name}(db: Session, id: int):
    """删除记录"""
    db_item = get_{name}(db, id)
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False
'''

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _to_pascal(name: str) -> str:
        """将 snake_case 转换为 PascalCase"""
        return "".join(word.capitalize() for word in name.split("_"))


__all__ = ["FastAPIEndpointGenerator"]
