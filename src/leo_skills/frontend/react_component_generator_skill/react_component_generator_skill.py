"""
react_component_generator_skill

React组件生成技能 - 生成 React 组件（Hooks + TypeScript），含类型定义、测试文件和样式。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class ReactComponentGenerator(BaseExecutor):
    """React组件生成器

    生成内容包括：
    - 组件文件（.tsx / .jsx）：含 Hooks、Props 解构、loading 状态等
    - 类型定义（.types.ts）：TypeScript 接口
    - 测试文件（.test.tsx）：Vitest + Testing Library
    - 样式文件（.css 或 styled-components）
    - 导出文件（index.ts）
    """

    def __init__(self, output_dir: str = ".", typescript: bool = True) -> None:
        self.name = "react_component_generator_skill"
        self.output_dir = Path(output_dir)
        self.typescript = typescript

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

        component_name = params.get("component_name", "MyComponent")
        props = params.get("props", [])
        hooks = params.get("hooks", ["useState"])
        features = params.get("features", [])
        save = params.get("save", False)

        if "typescript" in params:
            self.typescript = params["typescript"]

        result = self.generate(
            component_name=component_name,
            props=props,
            hooks=hooks,
            features=features,
        )

        if save:
            saved = self.save_files(component_name, result)
            return {
                "status": "success",
                "action": action,
                "data": result,
                "saved_files": {k: str(v) for k, v in saved.items()},
            }

        return {"status": "success", "action": action, "data": result}

    # ------------------------------------------------------------------ #
    #  核心生成逻辑
    # ------------------------------------------------------------------ #

    def generate(
        self,
        component_name: str,
        props: Optional[List[Dict[str, Any]]] = None,
        hooks: Optional[List[str]] = None,
        features: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """生成React组件

        Args:
            component_name: 组件名称（PascalCase）
            props: 属性定义列表，每项为 {'name': ..., 'type': ..., 'required': ..., 'description': ...}
            hooks: 使用的 React Hooks 列表
            features: 特性列表（如 'loading', 'styled'）

        Returns:
            生成的代码字典
        """
        props = props or []
        hooks = hooks or ["useState"]
        features = features or []

        results: Dict[str, str] = {}

        # 组件文件
        results["component"] = self._generate_component(component_name, props, hooks, features)

        # TypeScript 类型定义
        if self.typescript:
            results["types"] = self._generate_types(component_name, props)

        # 测试文件
        results["test"] = self._generate_test(component_name, props)

        # 样式文件
        if "styled" in features:
            results["styles"] = self._generate_styled(component_name)
        else:
            results["css"] = self._generate_css(component_name)

        return results

    # ------------------------------------------------------------------ #
    #  组件代码生成
    # ------------------------------------------------------------------ #

    def _generate_component(
        self,
        name: str,
        props: List[Dict[str, Any]],
        hooks: List[str],
        features: List[str],
    ) -> str:
        """生成 React 组件代码"""

        # 导入语句
        imports = ["import React"]
        hook_imports = [
            h for h in hooks
            if h in ["useState", "useEffect", "useCallback", "useMemo", "useRef", "useContext"]
        ]
        if hook_imports:
            imports[0] = f"import React, {{ {', '.join(hook_imports)} }} from 'react'"

        if "styled" in features:
            imports.append("import styled from 'styled-components'")
        else:
            imports.append(f"import './{name}.css'")

        if self.typescript:
            imports.append(f"import type {{ {name}Props }} from './{name}.types'")

        # Props 解构
        props_destructure = ""
        if props:
            prop_names = [p["name"] for p in props]
            props_destructure = f"{{ {', '.join(prop_names)} }}"

        # Hooks 使用代码
        hooks_code = []
        if "useState" in hooks:
            hooks_code.append("  const [state, setState] = useState(null)")
        if "useEffect" in hooks:
            hooks_code.append(
                "  useEffect(() => {\n"
                "    // 副作用逻辑\n"
                "    return () => {\n"
                "      // 清理函数\n"
                "    }\n"
                "  }, [])"
            )
        if "useCallback" in hooks:
            hooks_code.append(
                "  const handleClick = useCallback(() => {\n"
                "    // 处理点击\n"
                "  }, [])"
            )
        hooks_str = "\n\n".join(hooks_code) if hooks_code else ""

        # Loading 状态
        loading_code = ""
        if "loading" in features:
            loading_code = (
                "\n"
                '  if (loading) {\n'
                '    return <div className="loading">Loading...</div>\n'
                '  }\n'
            )

        # 类型注解
        type_annotation = f": React.FC<{name}Props>" if self.typescript else ""

        return f"""{chr(10).join(imports)}

/**
 * {name} 组件
 * Generated by Leo React Component Generator
 */
const {name}{type_annotation} = ({props_destructure}) => {{
{hooks_str}
{loading_code}
  return (
    <div className="{self._to_kebab_case(name)}">
      {{/* 组件内容 */}}
    </div>
  )
}}

export default {name}
"""

    # ------------------------------------------------------------------ #
    #  TypeScript 类型定义
    # ------------------------------------------------------------------ #

    def _generate_types(self, name: str, props: List[Dict[str, Any]]) -> str:
        """生成 TypeScript 类型定义文件"""
        lines = [f"// {name} 类型定义", ""]

        lines.append(f"export interface {name}Props {{")
        for prop in props:
            pname = prop["name"]
            ptype = self._map_ts_type(prop.get("type", "string"))
            required = prop.get("required", False)
            optional = "" if required else "?"
            desc = prop.get("description", "")
            if desc:
                lines.append(f"  /** {desc} */")
            lines.append(f"  {pname}{optional}: {ptype}")
        lines.append("}")

        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  测试文件
    # ------------------------------------------------------------------ #

    def _generate_test(self, name: str, props: List[Dict[str, Any]]) -> str:
        """生成 Vitest + Testing Library 测试文件"""
        props_mock = "{"
        for prop in props:
            pname = prop["name"]
            ptype = prop.get("type", "string")
            if ptype == "string":
                props_mock += f"\n      {pname}: 'test',"
            elif ptype == "number":
                props_mock += f"\n      {pname}: 1,"
            elif ptype == "boolean":
                props_mock += f"\n      {pname}: true,"
            else:
                props_mock += f"\n      {pname}: {{}},"
        props_mock += "\n    }" if props else "{}"

        return f"""import {{ render, screen }} from '@testing-library/react'
import {{ describe, it, expect }} from 'vitest'
import {name} from './{name}'

describe('{name}', () => {{
  it('renders without crashing', () => {{
    render(<{name} {{...{props_mock}}} />)
    expect(screen.getByRole('generic')).toBeInTheDocument()
  }})

  it('matches snapshot', () => {{
    const {{ container }} = render(<{name} {{...{props_mock}}} />)
    expect(container).toMatchSnapshot()
  }})
}})
"""

    # ------------------------------------------------------------------ #
    #  样式文件
    # ------------------------------------------------------------------ #

    def _generate_css(self, name: str) -> str:
        """生成普通 CSS 文件"""
        kebab = self._to_kebab_case(name)
        return f""".{kebab} {{
  /* 组件样式 */
}}

.{kebab} .loading {{
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100px;
}}
"""

    def _generate_styled(self, name: str) -> str:
        """生成 styled-components 样式文件"""
        return f"""import styled from 'styled-components'

export const {name}Wrapper = styled.div`
  /* 组件样式 */
`

export const LoadingWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100px;
`
"""

    # ------------------------------------------------------------------ #
    #  文件保存
    # ------------------------------------------------------------------ #

    def save_files(self, component_name: str, results: Dict[str, str]) -> Dict[str, Path]:
        """将生成的组件代码保存到文件

        Args:
            component_name: 组件名称
            results: generate() 返回的代码字典

        Returns:
            {文件类型: 文件路径} 的字典
        """
        comp_dir = self.output_dir / "components" / component_name
        comp_dir.mkdir(parents=True, exist_ok=True)

        saved: Dict[str, Path] = {}
        ext = "tsx" if self.typescript else "jsx"

        # 组件文件
        comp_path = comp_dir / f"{component_name}.{ext}"
        comp_path.write_text(results["component"], encoding="utf-8")
        saved["component"] = comp_path

        # 类型文件
        if "types" in results:
            types_path = comp_dir / f"{component_name}.types.ts"
            types_path.write_text(results["types"], encoding="utf-8")
            saved["types"] = types_path

        # 测试文件
        test_path = comp_dir / f"{component_name}.test.{ext}"
        test_path.write_text(results["test"], encoding="utf-8")
        saved["test"] = test_path

        # 样式文件
        if "css" in results:
            css_path = comp_dir / f"{component_name}.css"
            css_path.write_text(results["css"], encoding="utf-8")
            saved["css"] = css_path
        elif "styles" in results:
            styles_path = comp_dir / f"{component_name}.styles.ts"
            styles_path.write_text(results["styles"], encoding="utf-8")
            saved["styles"] = styles_path

        # 导出文件
        index_content = f"export {{ default }} from './{component_name}'\n"
        if "types" in results:
            index_content += f"export * from './{component_name}.types'\n"
        index_path = comp_dir / "index.ts"
        index_path.write_text(index_content, encoding="utf-8")
        saved["index"] = index_path

        return saved

    # ------------------------------------------------------------------ #
    #  工具方法
    # ------------------------------------------------------------------ #

    @staticmethod
    def _map_ts_type(ptype: str) -> str:
        """将简写类型映射为 TypeScript 类型"""
        type_map = {
            "string": "string",
            "number": "number",
            "boolean": "boolean",
            "array": "any[]",
            "object": "Record<string, any>",
            "function": "(...args: any[]) => void",
            "node": "React.ReactNode",
            "element": "React.ReactElement",
        }
        return type_map.get(ptype.lower(), "any")

    @staticmethod
    def _to_kebab_case(name: str) -> str:
        """将 PascalCase 转换为 kebab-case"""
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1).lower()


__all__ = ["ReactComponentGenerator"]
