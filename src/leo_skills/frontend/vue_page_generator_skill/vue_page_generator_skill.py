"""
vue_page_generator_skill

Vue页面生成技能 - 生成完整的 Vue3 页面（含路由配置、类型定义、Pinia Store）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class VuePageGenerator(BaseExecutor):
    """Vue3页面生成器

    生成内容包括：
    - 页面组件（.vue）：含布局、API 调用、响应式数据
    - TypeScript 类型定义：页面数据、查询参数、响应格式
    - 路由配置片段：可直接复制到 router/index.ts
    - Pinia Store 模块（可选）：状态管理
    """

    def __init__(self, output_dir: str = ".") -> None:
        self.name = "vue_page_generator_skill"
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "generate",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """执行技能入口

        Args:
            action: 动作类型，默认 "generate"
            context: 上下文参数
            **kwargs: 其他关键字参数
        """
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        page_name = params.get("page_name", "index")
        layout_type = params.get("layout_type", "default")
        api_endpoints = params.get("api_endpoints", [])
        features = params.get("features", [])

        result = self.generate(
            page_name=page_name,
            layout_type=layout_type,
            api_endpoints=api_endpoints,
            features=features,
        )

        return {"status": "success", "action": action, "data": result}

    # ------------------------------------------------------------------ #
    #  核心生成逻辑
    # ------------------------------------------------------------------ #

    def generate(
        self,
        page_name: str,
        layout_type: str = "default",
        api_endpoints: Optional[List[Dict[str, Any]]] = None,
        features: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """生成Vue3页面

        Args:
            page_name: 页面名称（snake_case）
            layout_type: 布局类型 (default/sidebar/dashboard)
            api_endpoints: API端点列表，每项为 {'method': ..., 'path': ..., 'name': ...}
            features: 功能特性列表（如 'store'）

        Returns:
            生成的代码字典
        """
        api_endpoints = api_endpoints or []
        features = features or []

        results: Dict[str, str] = {}
        results["page"] = self._generate_page(page_name, layout_type, api_endpoints, features)
        results["types"] = self._generate_types(page_name, api_endpoints)
        results["router"] = self._generate_router_config(page_name)

        if "store" in features:
            results["store"] = self._generate_store_module(page_name, api_endpoints)

        return results

    # ------------------------------------------------------------------ #
    #  页面组件生成
    # ------------------------------------------------------------------ #

    def _generate_page(
        self,
        name: str,
        layout: str,
        endpoints: List[Dict[str, Any]],
        features: List[str],
    ) -> str:
        """生成 Vue 页面组件"""
        pascal_name = "".join(word.capitalize() for word in name.split("_"))

        # 生成 API 调用代码
        api_imports = []
        api_calls = []
        for ep in endpoints:
            method = ep.get("method", "GET").lower()
            func_name = ep.get("name", f"{method}Data")
            api_imports.append(f"import {{ {func_name} }} from '@/api/{name}'")
            api_calls.append(
                f"\nconst {func_name}Result = ref(null)\n"
                f"const fetch{func_name.capitalize()} = async () => {{\n"
                f"  try {{\n"
                f"    {func_name}Result.value = await {func_name}()\n"
                f"  }} catch (error) {{\n"
                f"    console.error('API Error:', error)\n"
                f"  }}\n"
                f"}}"
            )

        api_imports_str = "\n".join(api_imports) if api_imports else ""
        api_calls_str = "\n".join(api_calls) if api_calls else ""

        # 布局模板
        layout_templates = {
            "default": '<div class="page-container">',
            "sidebar": '<div class="page-with-sidebar"><aside class="sidebar"></aside><main class="main-content">',
            "dashboard": '<div class="dashboard-layout"><header class="dashboard-header"></header><main class="dashboard-content">',
        }
        layout_open = layout_templates.get(layout, layout_templates["default"])
        layout_close = "</div>" if layout == "default" else "</main></div>"

        return f"""<template>
  {layout_open}
    <h1>{pascal_name}</h1>
    <div class="content">
      <!-- 页面内容 -->
    </div>
  {layout_close}
</template>

<script setup lang="ts">
import {{ ref, onMounted }} from 'vue'
import type {{ {pascal_name}Data }} from '@/types/{name}'
{api_imports_str}

// 响应式数据
const loading = ref(false)
const data = ref<{pascal_name}Data | null>(null)
{api_calls_str}

// 生命周期
onMounted(() => {{
  // 初始化逻辑
}})
</script>

<style scoped lang="scss">
.page-container {{
  padding: 20px;
}}

.content {{
  margin-top: 20px;
}}
</style>
"""

    # ------------------------------------------------------------------ #
    #  TypeScript 类型定义
    # ------------------------------------------------------------------ #

    def _generate_types(self, name: str, endpoints: List[Dict[str, Any]]) -> str:
        """生成页面相关的 TypeScript 类型定义"""
        pascal_name = "".join(word.capitalize() for word in name.split("_"))

        return f"""/**
 * {pascal_name} 页面类型定义
 * Generated by Leo Vue Page Generator
 */

export interface {pascal_name}Data {{
  id: number
  // 添加其他字段
}}

export interface {pascal_name}Query {{
  page?: number
  pageSize?: number
  // 添加查询参数
}}

export interface {pascal_name}Response {{
  data: {pascal_name}Data[]
  total: number
}}
"""

    # ------------------------------------------------------------------ #
    #  路由配置
    # ------------------------------------------------------------------ #

    def _generate_router_config(self, name: str) -> str:
        """生成路由配置片段（可直接复制到 router/index.ts）"""
        pascal_name = "".join(word.capitalize() for word in name.split("_"))
        kebab_name = name.replace("_", "-")

        return f"""// 添加到 router/index.ts
{{
  path: '/{kebab_name}',
  name: '{pascal_name}',
  component: () => import('@/views/{name}/{pascal_name}.vue'),
  meta: {{
    title: '{pascal_name}',
    requiresAuth: true
  }}
}}
"""

    # ------------------------------------------------------------------ #
    #  Pinia Store 模块
    # ------------------------------------------------------------------ #

    def _generate_store_module(self, name: str, endpoints: List[Dict[str, Any]]) -> str:
        """生成 Pinia Store 状态管理模块"""
        pascal_name = "".join(word.capitalize() for word in name.split("_"))

        return f"""import {{ defineStore }} from 'pinia'
import type {{ {pascal_name}Data }} from '@/types/{name}'

export const use{pascal_name}Store = defineStore('{name}', {{
  state: () => ({{
    data: null as {pascal_name}Data | null,
    list: [] as {pascal_name}Data[],
    loading: false,
    error: null as string | null
  }}),

  getters: {{
    isEmpty: (state) => state.list.length === 0
  }},

  actions: {{
    async fetchData() {{
      this.loading = true
      try {{
        // API调用
        this.loading = false
      }} catch (error) {{
        this.error = String(error)
        this.loading = false
      }}
    }}
  }}
}})
"""


__all__ = ["VuePageGenerator"]
