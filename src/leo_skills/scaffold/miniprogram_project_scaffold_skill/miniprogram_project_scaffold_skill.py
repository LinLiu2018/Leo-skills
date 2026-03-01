"""
微信小程序项目脚手架技能

生成微信小程序项目结构，包括 app.json、app.js、全局样式、
project.config.json、首页、工具函数，以及可选的云开发支持。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class MiniprogramScaffold(BaseExecutor):
    """微信小程序项目脚手架生成器。

    支持的操作：
        - generate: 生成项目结构（返回文件名→内容的字典）
        - save:     生成并写入磁盘
    """

    def __init__(self) -> None:
        self.name = "miniprogram_project_scaffold_skill"

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "generate",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        if action in ("generate", "run"):
            return self._action_generate(params)
        elif action == "save":
            return self._action_save(params)
        else:
            return {"status": "error", "message": f"未知操作: {action}"}

    # ------------------------------------------------------------------ #
    #  动作方法
    # ------------------------------------------------------------------ #

    def _action_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        project_name = params.get("project_name", "我的小程序")
        features: List[str] = params.get("features", [])
        with_cloud = params.get("with_cloud", False)

        files = self.generate(project_name, features, with_cloud)
        return {
            "status": "success",
            "action": "generate",
            "project_name": project_name,
            "files": list(files.keys()),
            "data": files,
        }

    def _action_save(self, params: Dict[str, Any]) -> Dict[str, Any]:
        project_name = params.get("project_name", "我的小程序")
        features: List[str] = params.get("features", [])
        with_cloud = params.get("with_cloud", False)
        output_dir = params.get("output_dir", ".")

        files = self.generate(project_name, features, with_cloud)
        saved = self._save_files(project_name, files, output_dir)
        return {
            "status": "success",
            "action": "save",
            "project_name": project_name,
            "files_saved": len(saved),
            "paths": {k: str(v) for k, v in saved.items()},
        }

    # ------------------------------------------------------------------ #
    #  核心生成逻辑
    # ------------------------------------------------------------------ #

    def generate(
        self,
        project_name: str,
        features: Optional[List[str]] = None,
        with_cloud: bool = False,
    ) -> Dict[str, str]:
        """生成小程序项目结构。"""
        features = features or []

        results = {
            "app.json": self._gen_app_json(project_name, features),
            "app.js": self._gen_app_js(),
            "app.wxss": self._gen_app_wxss(),
            "project.config.json": self._gen_project_config(project_name, with_cloud),
            "sitemap.json": self._gen_sitemap(),
            "pages/index/index.js": self._gen_index_page(),
            "pages/index/index.wxml": self._gen_index_wxml(project_name),
            "pages/index/index.wxss": self._gen_index_wxss(),
            "utils/util.js": self._gen_utils(),
        }

        if "user" in features:
            results["pages/user/user.js"] = self._gen_user_page()
            results["pages/user/user.wxml"] = self._gen_user_wxml()
            results["pages/user/user.wxss"] = self._gen_user_wxss()

        if with_cloud:
            results["cloudfunctions/getData/index.js"] = self._gen_cloud_function()
            results["cloudfunctions/getData/package.json"] = (
                '{\n  "name": "getData",\n  "version": "1.0.0",\n'
                '  "main": "index.js",\n'
                '  "dependencies": {\n    "wx-server-sdk": "~2.6.3"\n  }\n}\n'
            )

        return results

    def _save_files(
        self, project_name: str, files: Dict[str, str], output_dir: str
    ) -> Dict[str, Path]:
        saved: Dict[str, Path] = {}
        project_dir = Path(output_dir) / project_name
        for fp, content in files.items():
            full = project_dir / fp
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            saved[fp] = full
        return saved

    # ------------------------------------------------------------------ #
    #  模板方法
    # ------------------------------------------------------------------ #

    def _gen_app_json(self, name: str, features: List[str]) -> str:
        pages = ['"pages/index/index"', '"pages/logs/logs"']
        if "user" in features:
            pages.append('"pages/user/user"')
        pages_str = ",\n    ".join(pages)

        tab_bar = ""
        if "user" in features:
            tab_bar = """,
  "tabBar": {
    "color": "#999",
    "selectedColor": "#1890ff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "images/home.png",
        "selectedIconPath": "images/home-active.png"
      },
      {
        "pagePath": "pages/user/user",
        "text": "我的",
        "iconPath": "images/user.png",
        "selectedIconPath": "images/user-active.png"
      }
    ]
  }"""

        return f"""{{\n  "pages": [\n    {pages_str}\n  ],
  "window": {{
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#fff",
    "navigationBarTitleText": "{name}",
    "navigationBarTextStyle": "black"
  }}{tab_bar},
  "style": "v2",
  "sitemapLocation": "sitemap.json"
}}
"""

    def _gen_app_js(self) -> str:
        return """// app.js
App({
  onLaunch() {
    console.log('App onLaunch')
    const systemInfo = wx.getSystemInfoSync()
    this.globalData.systemInfo = systemInfo
  },

  globalData: {
    userInfo: null,
    systemInfo: null
  },

  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({ ...options, success: resolve, fail: reject })
    })
  }
})
"""

    def _gen_app_wxss(self) -> str:
        return """/* app.wxss - 全局样式 */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 28rpx;
  color: #333;
  background-color: #f5f5f5;
}

.container { padding: 20rpx; }
.flex { display: flex; }
.flex-center { display: flex; justify-content: center; align-items: center; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }

.btn-primary {
  background-color: #1890ff;
  color: #fff;
  border-radius: 8rpx;
  padding: 20rpx 40rpx;
}
"""

    def _gen_project_config(self, name: str, with_cloud: bool) -> str:
        cloud = '\n  "cloudfunctionRoot": "cloudfunctions/",' if with_cloud else ""
        return f"""{{\n  "miniprogramRoot": "miniprogram/",{cloud}
  "description": "{name}",
  "projectname": "{name}",
  "setting": {{
    "urlCheck": true, "es6": true, "enhance": true,
    "postcss": true, "minified": true, "newFeature": true
  }},
  "compileType": "miniprogram",
  "appid": "your-appid",
  "libVersion": "2.25.0"
}}
"""

    def _gen_sitemap(self) -> str:
        return '{\n  "rules": [{"action": "allow", "page": "*"}]\n}\n'

    def _gen_index_page(self) -> str:
        return "Page({\n  data: { motto: '欢迎使用小程序' },\n  onLoad() {},\n  onShow() {}\n})\n"

    def _gen_index_wxml(self, project_name: str) -> str:
        return f'<view class="container">\n  <text class="title">{project_name}</text>\n</view>\n'

    def _gen_index_wxss(self) -> str:
        return ".container { display:flex; flex-direction:column; align-items:center; padding-top:100rpx; }\n.title { font-size:36rpx; font-weight:bold; }\n"

    def _gen_user_page(self) -> str:
        return "Page({\n  data: { userInfo: null, hasLogin: false },\n  onLoad() {\n    const app = getApp()\n    if (app.globalData.userInfo) {\n      this.setData({ userInfo: app.globalData.userInfo, hasLogin: true })\n    }\n  }\n})\n"

    def _gen_user_wxml(self) -> str:
        return '<view class="container">\n  <image class="avatar" src="{{userInfo.avatarUrl}}" />\n  <text>{{userInfo.nickName || "未登录"}}</text>\n</view>\n'

    def _gen_user_wxss(self) -> str:
        return ".avatar { width:120rpx; height:120rpx; border-radius:50%; margin-bottom:20rpx; }\n"

    def _gen_utils(self) -> str:
        return """// utils/util.js
function formatTime(date) {
  const y = date.getFullYear(), m = date.getMonth()+1, d = date.getDate()
  const h = date.getHours(), mi = date.getMinutes(), s = date.getSeconds()
  const pad = n => n.toString().padStart(2, '0')
  return `${y}/${pad(m)}/${pad(d)} ${pad(h)}:${pad(mi)}:${pad(s)}`
}

function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

module.exports = { formatTime, debounce }
"""

    def _gen_cloud_function(self) -> str:
        return """const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event, context) => {
  const { collection, query } = event
  try {
    const result = await db.collection(collection).where(query).get()
    return { code: 0, data: result.data }
  } catch (error) {
    return { code: -1, error: error.message }
  }
}
"""


__all__ = ["MiniprogramScaffold"]
