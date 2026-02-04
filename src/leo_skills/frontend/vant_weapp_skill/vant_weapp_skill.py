"""
Vant Weapp Skill - 小程序UI组件库技能

基于有赞 Vant Weapp 的小程序 UI 组件生成技能。
GitHub: https://github.com/vant-ui/vant-weapp (18.3k stars)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.evolution import EvolvableSkill


class VantWeappSkill(EvolvableSkill):
    """
    Vant Weapp 小程序UI组件库技能

    支持快速生成符合微信设计规范的小程序页面和组件。
    """

    # 组件分类
    COMPONENTS = {
        "basic": ["button", "cell", "cell-group", "icon", "image", "col", "row", "popup", "toast", "transition"],
        "form": ["checkbox", "checkbox-group", "datetime-picker", "field", "picker", "radio", "radio-group",
                 "rate", "search", "slider", "stepper", "switch", "uploader"],
        "feedback": ["action-sheet", "dialog", "dropdown-menu", "dropdown-item", "loading", "notify",
                     "overlay", "share-sheet", "swipe-cell"],
        "display": ["badge", "card", "cell", "circle", "collapse", "collapse-item", "count-down",
                    "divider", "empty", "notice-bar", "panel", "progress", "skeleton", "steps", "sticky", "tag"],
        "navigation": ["grid", "grid-item", "index-bar", "index-anchor", "nav-bar", "sidebar",
                       "sidebar-item", "tab", "tabs", "tabbar", "tabbar-item", "tree-select"],
        "business": ["area", "calendar", "card", "goods-action", "goods-action-icon",
                     "goods-action-button", "submit-bar"]
    }

    # 页面模板
    PAGE_TEMPLATES = {
        "home": {
            "name": "首页模板",
            "components": ["nav-bar", "swiper", "grid", "card", "tabbar"]
        },
        "list": {
            "name": "列表页模板",
            "components": ["nav-bar", "search", "tabs", "card", "loading", "empty"]
        },
        "detail": {
            "name": "详情页模板",
            "components": ["nav-bar", "image", "cell-group", "cell", "button", "goods-action"]
        },
        "user": {
            "name": "个人中心模板",
            "components": ["nav-bar", "cell-group", "cell", "icon", "button"]
        },
        "gift-list": {
            "name": "礼品列表模板",
            "components": ["nav-bar", "card", "progress", "button", "empty", "loading"]
        },
        "form": {
            "name": "表单页模板",
            "components": ["nav-bar", "field", "picker", "switch", "button"]
        }
    }

    # 组件代码模板
    COMPONENT_TEMPLATES = {
        "button": {
            "wxml": '<van-button type="{type}" size="{size}" block="{block}">{text}</van-button>',
            "json": {"van-button": "@vant/weapp/button/index"},
            "props": {"type": "primary", "size": "normal", "block": False, "text": "按钮"}
        },
        "card": {
            "wxml": '''<van-card
  num="{num}"
  price="{price}"
  title="{title}"
  thumb="{thumb}"
  desc="{desc}"
/>''',
            "json": {"van-card": "@vant/weapp/card/index"},
            "props": {"num": "1", "price": "0.00", "title": "商品标题", "thumb": "", "desc": "描述"}
        },
        "cell": {
            "wxml": '<van-cell title="{title}" value="{value}" label="{label}" is-link="{isLink}" />',
            "json": {"van-cell": "@vant/weapp/cell/index"},
            "props": {"title": "单元格", "value": "内容", "label": "", "isLink": False}
        },
        "progress": {
            "wxml": '<van-progress percentage="{percentage}" stroke-width="{strokeWidth}" color="{color}" />',
            "json": {"van-progress": "@vant/weapp/progress/index"},
            "props": {"percentage": 50, "strokeWidth": 4, "color": "#FF6B35"}
        },
        "empty": {
            "wxml": '<van-empty image="{image}" description="{description}" />',
            "json": {"van-empty": "@vant/weapp/empty/index"},
            "props": {"image": "default", "description": "暂无数据"}
        },
        "loading": {
            "wxml": '<van-loading type="{type}" color="{color}" size="{size}" vertical>{text}</van-loading>',
            "json": {"van-loading": "@vant/weapp/loading/index"},
            "props": {"type": "circular", "color": "#FF6B35", "size": "24px", "text": "加载中..."}
        },
        "nav-bar": {
            "wxml": '<van-nav-bar title="{title}" left-text="{leftText}" left-arrow="{leftArrow}" bind:click-left="onClickLeft" />',
            "json": {"van-nav-bar": "@vant/weapp/nav-bar/index"},
            "props": {"title": "标题", "leftText": "返回", "leftArrow": True}
        },
        "tabbar": {
            "wxml": '''<van-tabbar active="{{ active }}" bind:change="onChange">
  <van-tabbar-item icon="home-o">首页</van-tabbar-item>
  <van-tabbar-item icon="search">分享</van-tabbar-item>
  <van-tabbar-item icon="friends-o">我的</van-tabbar-item>
</van-tabbar>''',
            "json": {
                "van-tabbar": "@vant/weapp/tabbar/index",
                "van-tabbar-item": "@vant/weapp/tabbar-item/index"
            },
            "props": {}
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        super().__init__("vant_weapp", Path(__file__).parent / "evolution.json")
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "config" / "config.yaml"

    def execute(self, action: str = "generate_component", **kwargs) -> Dict[str, Any]:
        """
        执行技能

        Args:
            action: 操作类型
                - generate_component: 生成单个组件
                - generate_page: 生成完整页面
                - get_example: 获取组件示例
                - list_components: 列出所有组件
                - list_templates: 列出所有页面模板
            component: 组件名称
            template: 页面模板名称
            props: 组件属性
            theme_color: 主题色

        Returns:
            执行结果
        """
        if action == "generate_component":
            return self._generate_component(**kwargs)
        elif action == "generate_page":
            return self._generate_page(**kwargs)
        elif action == "get_example":
            return self._get_example(**kwargs)
        elif action == "list_components":
            return {"success": True, "components": self.COMPONENTS}
        elif action == "list_templates":
            return {"success": True, "templates": self.PAGE_TEMPLATES}
        elif action == "get_install_guide":
            return self._get_install_guide()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def _generate_component(
        self,
        component: str,
        props: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成单个组件代码"""
        if component not in self.COMPONENT_TEMPLATES:
            return {
                "success": False,
                "error": f"Unknown component: {component}",
                "available": list(self.COMPONENT_TEMPLATES.keys())
            }

        template = self.COMPONENT_TEMPLATES[component]
        merged_props = {**template["props"], **(props or {})}

        # 生成 WXML
        wxml = template["wxml"]
        for key, value in merged_props.items():
            wxml = wxml.replace("{" + key + "}", str(value))

        self.learn(f"Generated component: {component}")

        return {
            "success": True,
            "component": component,
            "wxml": wxml,
            "json_config": template["json"],
            "props": merged_props
        }

    def _generate_page(
        self,
        template: str,
        page_name: str = "page",
        theme_color: str = "#FF6B35",
        **kwargs
    ) -> Dict[str, Any]:
        """生成完整页面"""
        if template not in self.PAGE_TEMPLATES:
            return {
                "success": False,
                "error": f"Unknown template: {template}",
                "available": list(self.PAGE_TEMPLATES.keys())
            }

        page_template = self.PAGE_TEMPLATES[template]
        components = page_template["components"]

        # 收集所有组件的 JSON 配置
        json_config = {}
        wxml_parts = []

        for comp in components:
            if comp in self.COMPONENT_TEMPLATES:
                comp_template = self.COMPONENT_TEMPLATES[comp]
                json_config.update(comp_template["json"])

                # 替换主题色
                wxml = comp_template["wxml"]
                wxml = wxml.replace("#FF6B35", theme_color)
                wxml_parts.append(f"<!-- {comp} -->\n{wxml}")

        self.learn(f"Generated page: {template}")

        return {
            "success": True,
            "template": template,
            "page_name": page_name,
            "wxml": "\n\n".join(wxml_parts),
            "json_config": {
                "usingComponents": json_config
            },
            "theme_color": theme_color,
            "components_used": components
        }

    def _get_example(self, component: str, **kwargs) -> Dict[str, Any]:
        """获取组件使用示例"""
        if component not in self.COMPONENT_TEMPLATES:
            return {
                "success": False,
                "error": f"Unknown component: {component}"
            }

        template = self.COMPONENT_TEMPLATES[component]

        return {
            "success": True,
            "component": component,
            "example": {
                "wxml": template["wxml"],
                "json": template["json"],
                "default_props": template["props"]
            },
            "docs_url": f"https://vant-contrib.gitee.io/vant-weapp/#/zh-CN/{component}"
        }

    def _get_install_guide(self) -> Dict[str, Any]:
        """获取安装指南"""
        return {
            "success": True,
            "guide": {
                "step1": {
                    "title": "安装 npm 包",
                    "command": "npm i @vant/weapp -S --production"
                },
                "step2": {
                    "title": "修改 app.json",
                    "note": "将 app.json 中的 \"style\": \"v2\" 去除"
                },
                "step3": {
                    "title": "修改 project.config.json",
                    "config": {
                        "setting": {
                            "packNpmManually": True,
                            "packNpmRelationList": [{
                                "packageJsonPath": "./package.json",
                                "miniprogramNpmDistDir": "./miniprogram/"
                            }]
                        }
                    }
                },
                "step4": {
                    "title": "构建 npm",
                    "note": "在微信开发者工具中点击 工具 -> 构建 npm"
                }
            }
        }


# 便捷函数
def generate_vant_component(component: str, props: Dict = None) -> Dict[str, Any]:
    """快速生成 Vant 组件"""
    skill = VantWeappSkill()
    return skill.execute(action="generate_component", component=component, props=props)


def generate_vant_page(template: str, theme_color: str = "#FF6B35") -> Dict[str, Any]:
    """快速生成 Vant 页面"""
    skill = VantWeappSkill()
    return skill.execute(action="generate_page", template=template, theme_color=theme_color)
