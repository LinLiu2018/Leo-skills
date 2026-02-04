"""
WeUI Miniprogram Skill - 微信官方小程序组件库技能

基于微信官方 WeUI Miniprogram 的小程序 UI 组件生成技能。
GitHub: https://github.com/wechat-miniprogram/weui-miniprogram (2.4k stars)
"""

from pathlib import Path
from typing import Any, Dict, Optional

from leo_skills.core.evolution import EvolvableSkill


class WeuiMiniprogramSkill(EvolvableSkill):
    """
    WeUI Miniprogram 微信官方小程序组件库技能

    提供与微信原生视觉体验一致的组件生成能力。
    """

    # 组件分类
    COMPONENTS = {
        "form": ["mp-form", "mp-cells", "mp-cell", "mp-checkbox-group", "mp-checkbox",
                 "mp-uploader", "mp-slider", "mp-toptips"],
        "basic": ["mp-badge", "mp-loading", "mp-icon", "mp-searchbar"],
        "feedback": ["mp-actionsheet", "mp-dialog", "mp-half-screen-dialog", "mp-msg", "mp-toast"],
        "navigation": ["mp-navigation-bar", "mp-tabbar"],
        "display": ["mp-gallery", "mp-slideview"]
    }

    # 组件代码模板
    COMPONENT_TEMPLATES = {
        "mp-cell": {
            "wxml": '''<mp-cell title="{title}" value="{value}" footer="{footer}" link="{link}" ext-class="{extClass}">
  <view slot="icon" wx:if="{{icon}}"><mp-icon icon="{icon}" size="24"/></view>
</mp-cell>''',
            "json": {"mp-cell": "weui-miniprogram/cell/cell"},
            "props": {"title": "单元格", "value": "", "footer": "", "link": False, "icon": "", "extClass": ""}
        },
        "mp-cells": {
            "wxml": '''<mp-cells title="{title}" ext-class="{extClass}">
  {children}
</mp-cells>''',
            "json": {"mp-cells": "weui-miniprogram/cells/cells"},
            "props": {"title": "", "extClass": "", "children": ""}
        },
        "mp-form": {
            "wxml": '''<mp-form id="form" rules="{{rules}}" models="{{formData}}">
  <mp-cells>
    {children}
  </mp-cells>
  <view class="weui-btn-area">
    <button class="weui-btn" type="primary" bindtap="submitForm">提交</button>
  </view>
</mp-form>''',
            "json": {
                "mp-form": "weui-miniprogram/form/form",
                "mp-cells": "weui-miniprogram/cells/cells"
            },
            "props": {"children": ""}
        },
        "mp-dialog": {
            "wxml": '''<mp-dialog title="{title}" show="{{showDialog}}" bindbuttontap="tapDialogButton" buttons="{{buttons}}">
  <view>{content}</view>
</mp-dialog>''',
            "json": {"mp-dialog": "weui-miniprogram/dialog/dialog"},
            "props": {"title": "提示", "content": "确定要执行此操作吗？"}
        },
        "mp-actionsheet": {
            "wxml": '''<mp-actionsheet show="{{showActionsheet}}" actions="{{actions}}" title="{title}" bindactiontap="actionTap"/>''',
            "json": {"mp-actionsheet": "weui-miniprogram/actionsheet/actionsheet"},
            "props": {"title": ""}
        },
        "mp-toptips": {
            "wxml": '<mp-toptips msg="{msg}" type="{type}" show="{{showToptips}}"/>',
            "json": {"mp-toptips": "weui-miniprogram/toptips/toptips"},
            "props": {"msg": "提示信息", "type": "error"}
        },
        "mp-toast": {
            "wxml": '<mp-toast icon="{icon}" show="{{showToast}}">{text}</mp-toast>',
            "json": {"mp-toast": "weui-miniprogram/toast/toast"},
            "props": {"icon": "success", "text": "操作成功"}
        },
        "mp-loading": {
            "wxml": '<mp-loading type="{type}" show="{{showLoading}}" tips="{tips}"/>',
            "json": {"mp-loading": "weui-miniprogram/loading/loading"},
            "props": {"type": "circle", "tips": "加载中..."}
        },
        "mp-badge": {
            "wxml": '<mp-badge content="{content}" ext-class="{extClass}">{children}</mp-badge>',
            "json": {"mp-badge": "weui-miniprogram/badge/badge"},
            "props": {"content": "", "extClass": "", "children": ""}
        },
        "mp-searchbar": {
            "wxml": '''<mp-searchbar
  value="{{searchValue}}"
  placeholder="{placeholder}"
  search="{{search}}"
  bindsearch="onSearch"
  bindinput="onInput"
  bindclear="onClear"
/>''',
            "json": {"mp-searchbar": "weui-miniprogram/searchbar/searchbar"},
            "props": {"placeholder": "搜索"}
        },
        "mp-navigation-bar": {
            "wxml": '<mp-navigation-bar title="{title}" back="{{canBack}}" color="{color}" background="{background}"/>',
            "json": {"mp-navigation-bar": "weui-miniprogram/navigation-bar/navigation-bar"},
            "props": {"title": "页面标题", "color": "#000000", "background": "#ffffff"}
        },
        "mp-tabbar": {
            "wxml": '''<mp-tabbar current="{{current}}" list="{{tabList}}" bindchange="tabChange"/>''',
            "json": {"mp-tabbar": "weui-miniprogram/tabbar/tabbar"},
            "props": {}
        },
        "mp-half-screen-dialog": {
            "wxml": '''<mp-half-screen-dialog show="{{show}}" title="{title}" sub-title="{subTitle}" desc="{desc}" tips="{tips}" buttons="{{buttons}}">
  {children}
</mp-half-screen-dialog>''',
            "json": {"mp-half-screen-dialog": "weui-miniprogram/half-screen-dialog/half-screen-dialog"},
            "props": {"title": "标题", "subTitle": "", "desc": "", "tips": "", "children": ""}
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        super().__init__("weui_miniprogram", Path(__file__).parent / "evolution.json")
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "config" / "config.yaml"

    def execute(self, action: str = "generate_component", **kwargs) -> Dict[str, Any]:
        """
        执行技能

        Args:
            action: 操作类型
                - generate_component: 生成单个组件
                - list_components: 列出所有组件
                - get_example: 获取组件示例
                - get_install_guide: 获取安装指南
            component: 组件名称
            props: 组件属性
            dark_mode: 是否启用深色模式

        Returns:
            执行结果
        """
        if action == "generate_component":
            return self._generate_component(**kwargs)
        elif action == "list_components":
            return {"success": True, "components": self.COMPONENTS}
        elif action == "get_example":
            return self._get_example(**kwargs)
        elif action == "get_install_guide":
            return self._get_install_guide()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def _generate_component(
        self,
        component: str,
        props: Dict[str, Any] = None,
        dark_mode: bool = False,
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

        # 添加深色模式支持
        if dark_mode:
            wxml = f'<view data-weui-theme="dark">\n{wxml}\n</view>'

        self.learn(f"Generated WeUI component: {component}")

        return {
            "success": True,
            "component": component,
            "wxml": wxml,
            "json_config": template["json"],
            "props": merged_props,
            "dark_mode": dark_mode
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
            "docs_url": "https://wechat-miniprogram.github.io/weui/docs/"
        }

    def _get_install_guide(self) -> Dict[str, Any]:
        """获取安装指南"""
        return {
            "success": True,
            "guide": {
                "step1": {
                    "title": "安装 npm 包",
                    "command": "npm install weui-miniprogram"
                },
                "step2": {
                    "title": "在 app.wxss 中引入样式",
                    "code": "@import 'weui-miniprogram/weui-wxss/dist/style/weui.wxss';"
                },
                "step3": {
                    "title": "构建 npm",
                    "note": "在微信开发者工具中点击 工具 -> 构建 npm"
                },
                "step4": {
                    "title": "在页面 json 中引入组件",
                    "example": {
                        "usingComponents": {
                            "mp-cell": "weui-miniprogram/cell/cell",
                            "mp-cells": "weui-miniprogram/cells/cells"
                        }
                    }
                }
            },
            "dark_mode_tip": "添加 data-weui-theme=\"dark\" 属性启用深色模式"
        }


# 便捷函数
def generate_weui_component(component: str, props: Dict = None, dark_mode: bool = False) -> Dict[str, Any]:
    """快速生成 WeUI 组件"""
    skill = WeuiMiniprogramSkill()
    return skill.execute(action="generate_component", component=component, props=props, dark_mode=dark_mode)
