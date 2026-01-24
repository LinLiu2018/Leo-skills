"""
微信小程序项目脚手架 Skill
========================
生成微信小程序项目结构
"""

from pathlib import Path
from typing import Dict, List, Optional


class MiniprogramProjectScaffold:
    """微信小程序项目脚手架"""

    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)

    def generate(
        self,
        project_name: str,
        features: List[str] = None,
        with_cloud: bool = False
    ) -> Dict[str, str]:
        """
        生成小程序项目结构

        Args:
            project_name: 项目名称
            features: 功能特性列表
            with_cloud: 是否包含云开发

        Returns:
            生成的文件字典
        """
        features = features or []

        results = {
            'app_json': self._generate_app_json(project_name, features),
            'app_js': self._generate_app_js(),
            'app_wxss': self._generate_app_wxss(),
            'project_config': self._generate_project_config(project_name, with_cloud),
            'sitemap': self._generate_sitemap(),
            'index_page': self._generate_index_page(),
            'utils': self._generate_utils()
        }

        if with_cloud:
            results['cloud_function'] = self._generate_cloud_function()

        return results

    def _generate_app_json(self, name: str, features: List[str]) -> str:
        """生成app.json"""
        pages = [
            "pages/index/index",
            "pages/logs/logs"
        ]

        if 'user' in features:
            pages.append("pages/user/user")

        return '''{
  "pages": ''' + str(pages).replace("'", '"') + ''',
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#fff",
    "navigationBarTitleText": "''' + name + '''",
    "navigationBarTextStyle": "black"
  },
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
  },
  "style": "v2",
  "sitemapLocation": "sitemap.json"
}
'''

    def _generate_app_js(self) -> str:
        """生成app.js"""
        return '''// app.js
App({
  onLaunch() {
    // 小程序初始化
    console.log('App onLaunch')

    // 获取系统信息
    const systemInfo = wx.getSystemInfoSync()
    this.globalData.systemInfo = systemInfo
  },

  globalData: {
    userInfo: null,
    systemInfo: null
  },

  // 工具方法
  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        ...options,
        success: resolve,
        fail: reject
      })
    })
  }
})
'''

    def _generate_app_wxss(self) -> str:
        """生成app.wxss"""
        return '''/* app.wxss - 全局样式 */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 28rpx;
  color: #333;
  background-color: #f5f5f5;
}

.container {
  padding: 20rpx;
}

.flex {
  display: flex;
}

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-primary {
  background-color: #1890ff;
  color: #fff;
  border-radius: 8rpx;
  padding: 20rpx 40rpx;
}
'''

    def _generate_project_config(self, name: str, with_cloud: bool) -> str:
        """生成project.config.json"""
        cloud_config = '''
  "cloudfunctionRoot": "cloudfunctions/",''' if with_cloud else ''

        return '''{
  "miniprogramRoot": "miniprogram/",''' + cloud_config + '''
  "description": "''' + name + '''",
  "projectname": "''' + name + '''",
  "setting": {
    "urlCheck": true,
    "es6": true,
    "enhance": true,
    "postcss": true,
    "minified": true,
    "newFeature": true
  },
  "compileType": "miniprogram",
  "appid": "your-appid",
  "libVersion": "2.25.0"
}
'''

    def _generate_sitemap(self) -> str:
        """生成sitemap.json"""
        return '''{
  "desc": "关于本文件的更多信息，请参考文档 https://developers.weixin.qq.com/miniprogram/dev/framework/sitemap.html",
  "rules": [{
    "action": "allow",
    "page": "*"
  }]
}
'''

    def _generate_index_page(self) -> str:
        """生成首页"""
        return '''// pages/index/index.js
Page({
  data: {
    motto: '欢迎使用小程序'
  },

  onLoad() {
    // 页面加载
  },

  onShow() {
    // 页面显示
  }
})
'''

    def _generate_utils(self) -> str:
        """生成工具函数"""
        return '''// utils/util.js

/**
 * 格式化时间
 */
function formatTime(date) {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return `${[year, month, day].map(formatNumber).join('/')} ${[hour, minute, second].map(formatNumber).join(':')}`
}

function formatNumber(n) {
  n = n.toString()
  return n[1] ? n : `0${n}`
}

/**
 * 防抖函数
 */
function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

module.exports = {
  formatTime,
  debounce
}
'''

    def _generate_cloud_function(self) -> str:
        """生成云函数示例"""
        return '''// cloudfunctions/getData/index.js
const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const db = cloud.database()

exports.main = async (event, context) => {
  const { collection, query } = event

  try {
    const result = await db.collection(collection).where(query).get()
    return {
      code: 0,
      data: result.data
    }
  } catch (error) {
    return {
      code: -1,
      error: error.message
    }
  }
}
'''


def main():
    """示例用法"""
    generator = MiniprogramProjectScaffold(output_dir="./output")

    results = generator.generate(
        project_name='我的小程序',
        features=['user', 'share'],
        with_cloud=True
    )

    print("生成完成！")
    for name in results.keys():
        print(f"  - {name}")


if __name__ == '__main__':
    main()
