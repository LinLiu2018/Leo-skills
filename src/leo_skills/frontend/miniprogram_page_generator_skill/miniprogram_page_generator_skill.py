"""
miniprogram_page_generator_skill

微信小程序页面生成技能 - 自动生成小程序页面代码，支持表单页、列表页、详情页、分享页等类型。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class MiniprogramPageGenerator(BaseExecutor):
    """微信小程序页面生成器

    支持的页面类型：
    - form: 表单页面（含输入验证和提交）
    - list: 列表页面（含分页加载和下拉刷新）
    - detail: 详情页面
    - share: 分享裂变页面（含邀请、海报等功能）
    - basic: 基础页面
    """

    def __init__(self, output_dir: str = ".") -> None:
        self.name = "miniprogram_page_generator_skill"
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
        page_type = params.get("page_type", "form")
        data_bindings = params.get("data_bindings", [])
        api_endpoints = params.get("api_endpoints", [])
        features = params.get("features", [])
        save = params.get("save", False)

        result = self.generate(
            page_name=page_name,
            page_type=page_type,
            data_bindings=data_bindings,
            api_endpoints=api_endpoints,
            features=features,
        )

        if save:
            saved = self.save_files(page_name, result)
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
        page_name: str,
        page_type: str = "form",
        data_bindings: Optional[List[Dict[str, Any]]] = None,
        api_endpoints: Optional[List[Dict[str, Any]]] = None,
        features: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """生成小程序页面代码

        Args:
            page_name: 页面名称
            page_type: 页面类型 (form/list/detail/share/basic)
            data_bindings: 数据绑定字段列表
            api_endpoints: API端点配置列表
            features: 特性列表（如 '下拉刷新', '分享' 等）

        Returns:
            {'wxml': ..., 'wxss': ..., 'js': ..., 'json': ...} 代码字典
        """
        data_bindings = data_bindings or []
        api_endpoints = api_endpoints or []
        features = features or []

        type_generators = {
            "form": self._generate_form_page,
            "list": self._generate_list_page,
            "detail": self._generate_detail_page,
            "share": self._generate_share_page,
        }

        generator = type_generators.get(page_type)
        if generator:
            if page_type in ("form", "list"):
                results = generator(page_name, data_bindings, api_endpoints)
            elif page_type == "detail":
                results = generator(page_name, data_bindings)
            elif page_type == "share":
                results = generator(page_name, data_bindings, features)
        else:
            results = self._generate_basic_page(page_name)

        # 追加 JSON 配置
        results["json"] = self._generate_json(page_name, features)
        return results

    # ------------------------------------------------------------------ #
    #  表单页面
    # ------------------------------------------------------------------ #

    def _generate_form_page(
        self,
        page_name: str,
        fields: List[Dict[str, Any]],
        api_endpoints: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """生成表单页面（含输入框、选择器、提交逻辑）"""

        # --- WXML ---
        form_items = []
        for field in fields:
            name = field.get("name", "")
            label = field.get("label", name)
            input_type = field.get("type", "text")

            if input_type == "select":
                form_items.append(
                    f'  <view class="form-item">\n'
                    f'    <text class="label">{label}</text>\n'
                    f'    <picker mode="selector" range="{{{{options.{name}}}}}" '
                    f'bindchange="on{name.capitalize()}Change">\n'
                    f"      <view class=\"picker\">{{{{formData.{name} || '请选择'}}}}</view>\n"
                    f"    </picker>\n"
                    f"  </view>"
                )
            else:
                form_items.append(
                    f'  <view class="form-item">\n'
                    f'    <text class="label">{label}</text>\n'
                    f'    <input type="{input_type}" placeholder="请输入{label}" '
                    f'value="{{{{formData.{name}}}}}" bindinput="onInput" data-field="{name}" />\n'
                    f"  </view>"
                )

        wxml = f"""<!--{page_name}.wxml-->
<view class="container">
  <view class="header">
    <text class="title">{{{{pageTitle}}}}</text>
  </view>

  <form bindsubmit="onSubmit">
{chr(10).join(form_items)}

    <button class="submit-btn" form-type="submit" loading="{{{{loading}}}}">
      {{{{loading ? '提交中...' : '立即提交'}}}}
    </button>
  </form>
</view>
"""

        # --- WXSS ---
        wxss = f"""/* {page_name}.wxss */
.container {{
  padding: 30rpx;
  background: #f5f5f5;
  min-height: 100vh;
}}

.header {{
  text-align: center;
  margin-bottom: 40rpx;
}}

.title {{
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}}

.form-item {{
  background: #fff;
  padding: 30rpx;
  margin-bottom: 20rpx;
  border-radius: 12rpx;
}}

.label {{
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 16rpx;
}}

input {{
  width: 100%;
  height: 80rpx;
  font-size: 32rpx;
  border-bottom: 1rpx solid #eee;
}}

.picker {{
  height: 80rpx;
  line-height: 80rpx;
  font-size: 32rpx;
  color: #333;
  border-bottom: 1rpx solid #eee;
}}

.submit-btn {{
  margin-top: 60rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 50rpx;
  font-size: 32rpx;
  height: 90rpx;
  line-height: 90rpx;
}}
"""

        # --- JS ---
        data_init = ", ".join([f"'{f.get('name', '')}': ''" for f in fields])
        api_url = api_endpoints[0].get("url", "/api/submit") if api_endpoints else "/api/submit"

        js = f"""// {page_name}.js
const app = getApp()

Page({{
  data: {{
    pageTitle: '信息填写',
    formData: {{ {data_init} }},
    loading: false,
    options: {{}}
  }},

  onLoad(options) {{
    // 获取URL参数（如推荐人ID）
    if (options.pid) {{
      this.setData({{ 'formData.parent_id': options.pid }})
    }}
  }},

  // 输入框变化
  onInput(e) {{
    const field = e.currentTarget.dataset.field
    this.setData({{
      [`formData.${{field}}`]: e.detail.value
    }})
  }},

  // 表单提交
  async onSubmit(e) {{
    const {{ formData }} = this.data

    // 验证
    if (!this.validateForm(formData)) {{
      return
    }}

    this.setData({{ loading: true }})

    try {{
      const res = await wx.request({{
        url: app.globalData.baseUrl + '{api_url}',
        method: 'POST',
        data: formData
      }})

      if (res.data.success) {{
        wx.showToast({{ title: '提交成功', icon: 'success' }})
        // 跳转到结果页
        wx.navigateTo({{
          url: `/pages/result/result?id=${{res.data.data.id}}`
        }})
      }} else {{
        wx.showToast({{ title: res.data.error || '提交失败', icon: 'none' }})
      }}
    }} catch (err) {{
      wx.showToast({{ title: '网络错误', icon: 'none' }})
    }} finally {{
      this.setData({{ loading: false }})
    }}
  }},

  // 表单验证
  validateForm(data) {{
    if (!data.name) {{
      wx.showToast({{ title: '请输入姓名', icon: 'none' }})
      return false
    }}
    if (!data.phone || !/^1[3-9]\\d{{9}}$/.test(data.phone)) {{
      wx.showToast({{ title: '请输入正确的手机号', icon: 'none' }})
      return false
    }}
    return true
  }}
}})
"""

        return {"wxml": wxml, "wxss": wxss, "js": js}

    # ------------------------------------------------------------------ #
    #  列表页面
    # ------------------------------------------------------------------ #

    def _generate_list_page(
        self,
        page_name: str,
        fields: List[Dict[str, Any]],
        api_endpoints: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """生成列表页面（含分页、下拉刷新、触底加载）"""

        wxml = f"""<!--{page_name}.wxml-->
<view class="container">
  <view class="list">
    <view class="list-item" wx:for="{{{{list}}}}" wx:key="id" bindtap="onItemTap" data-id="{{{{item.id}}}}">
      <view class="item-content">
        <text class="item-title">{{{{item.name}}}}</text>
        <text class="item-desc">{{{{item.description}}}}</text>
      </view>
      <view class="item-arrow">></view>
    </view>
  </view>

  <view class="loading" wx:if="{{{{loading}}}}">
    <text>加载中...</text>
  </view>

  <view class="empty" wx:if="{{{{!loading && list.length === 0}}}}">
    <text>暂无数据</text>
  </view>
</view>
"""

        wxss = f"""/* {page_name}.wxss */
.container {{
  padding: 20rpx;
  background: #f5f5f5;
  min-height: 100vh;
}}

.list-item {{
  display: flex;
  align-items: center;
  background: #fff;
  padding: 30rpx;
  margin-bottom: 20rpx;
  border-radius: 12rpx;
}}

.item-content {{
  flex: 1;
}}

.item-title {{
  font-size: 32rpx;
  color: #333;
  display: block;
}}

.item-desc {{
  font-size: 26rpx;
  color: #999;
  margin-top: 10rpx;
  display: block;
}}

.item-arrow {{
  color: #ccc;
  font-size: 28rpx;
}}

.loading, .empty {{
  text-align: center;
  padding: 60rpx;
  color: #999;
}}
"""

        api_url = api_endpoints[0].get("url", "/api/list") if api_endpoints else "/api/list"

        js = f"""// {page_name}.js
const app = getApp()

Page({{
  data: {{
    list: [],
    loading: false,
    page: 1,
    hasMore: true
  }},

  onLoad() {{
    this.loadData()
  }},

  onPullDownRefresh() {{
    this.setData({{ page: 1, hasMore: true }})
    this.loadData().then(() => wx.stopPullDownRefresh())
  }},

  onReachBottom() {{
    if (this.data.hasMore && !this.data.loading) {{
      this.loadData()
    }}
  }},

  async loadData() {{
    this.setData({{ loading: true }})

    try {{
      const res = await wx.request({{
        url: app.globalData.baseUrl + '{api_url}',
        data: {{ page: this.data.page }}
      }})

      if (res.data.success) {{
        const newList = this.data.page === 1 ? res.data.data : [...this.data.list, ...res.data.data]
        this.setData({{
          list: newList,
          page: this.data.page + 1,
          hasMore: res.data.data.length > 0
        }})
      }}
    }} catch (err) {{
      wx.showToast({{ title: '加载失败', icon: 'none' }})
    }} finally {{
      this.setData({{ loading: false }})
    }}
  }},

  onItemTap(e) {{
    const id = e.currentTarget.dataset.id
    wx.navigateTo({{ url: `/pages/detail/detail?id=${{id}}` }})
  }}
}})
"""

        return {"wxml": wxml, "wxss": wxss, "js": js}

    # ------------------------------------------------------------------ #
    #  详情页面
    # ------------------------------------------------------------------ #

    def _generate_detail_page(
        self,
        page_name: str,
        data_bindings: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """生成详情页面"""

        wxml = f"""<!--{page_name}.wxml-->
<view class="container">
  <view class="detail-card">
    <view class="detail-item" wx:for="{{{{details}}}}" wx:key="key">
      <text class="label">{{{{item.label}}}}</text>
      <text class="value">{{{{item.value}}}}</text>
    </view>
  </view>
</view>
"""

        wxss = f"""/* {page_name}.wxss */
.container {{ padding: 30rpx; background: #f5f5f5; min-height: 100vh; }}
.detail-card {{ background: #fff; border-radius: 12rpx; padding: 30rpx; }}
.detail-item {{ display: flex; justify-content: space-between; padding: 20rpx 0; border-bottom: 1rpx solid #eee; }}
.label {{ color: #666; font-size: 28rpx; }}
.value {{ color: #333; font-size: 28rpx; }}
"""

        js = f"""// {page_name}.js
Page({{
  data: {{ details: [] }},
  onLoad(options) {{
    if (options.id) this.loadDetail(options.id)
  }},
  async loadDetail(id) {{
    // TODO: 加载详情数据
  }}
}})
"""

        return {"wxml": wxml, "wxss": wxss, "js": js}

    # ------------------------------------------------------------------ #
    #  分享裂变页面
    # ------------------------------------------------------------------ #

    def _generate_share_page(
        self,
        page_name: str,
        data_bindings: List[Dict[str, Any]],
        features: List[str],
    ) -> Dict[str, str]:
        """生成分享裂变页面（含优惠券展示、邀请记录、分享/海报功能）"""

        wxml = f"""<!--{page_name}.wxml-->
<view class="container">
  <view class="card">
    <view class="coupon-info">
      <text class="coupon-value">{{{{couponValue}}}}元</text>
      <text class="coupon-desc">优惠券</text>
    </view>

    <view class="user-info">
      <text class="invite-count">已邀请 {{{{inviteCount}}}} 人</text>
    </view>
  </view>

  <view class="share-section">
    <text class="share-title">分享给好友，再得优惠券</text>

    <button class="share-btn" open-type="share">
      分享给好友
    </button>

    <button class="poster-btn" bindtap="generatePoster">
      生成海报
    </button>
  </view>

  <view class="invite-list" wx:if="{{{{inviteList.length > 0}}}}">
    <text class="list-title">邀请记录</text>
    <view class="invite-item" wx:for="{{{{inviteList}}}}" wx:key="id">
      <text>{{{{item.name}}}}</text>
      <text class="invite-time">{{{{item.time}}}}</text>
    </view>
  </view>
</view>
"""

        wxss = f"""/* {page_name}.wxss */
.container {{
  padding: 30rpx;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}}

.card {{
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  text-align: center;
}}

.coupon-value {{
  font-size: 72rpx;
  font-weight: bold;
  color: #ff4757;
}}

.coupon-desc {{
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-top: 10rpx;
}}

.invite-count {{
  display: block;
  margin-top: 30rpx;
  font-size: 28rpx;
  color: #333;
}}

.share-section {{
  margin-top: 40rpx;
  text-align: center;
}}

.share-title {{
  color: #fff;
  font-size: 30rpx;
  display: block;
  margin-bottom: 30rpx;
}}

.share-btn, .poster-btn {{
  width: 80%;
  height: 90rpx;
  line-height: 90rpx;
  border-radius: 45rpx;
  font-size: 32rpx;
  margin-bottom: 20rpx;
}}

.share-btn {{
  background: #07c160;
  color: #fff;
}}

.poster-btn {{
  background: #fff;
  color: #333;
}}

.invite-list {{
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-top: 40rpx;
}}

.list-title {{
  font-size: 30rpx;
  font-weight: bold;
  display: block;
  margin-bottom: 20rpx;
}}

.invite-item {{
  display: flex;
  justify-content: space-between;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #eee;
  font-size: 28rpx;
}}

.invite-time {{
  color: #999;
}}
"""

        js = f"""// {page_name}.js
const app = getApp()

Page({{
  data: {{
    couponValue: 10,
    inviteCount: 0,
    inviteList: [],
    userId: null
  }},

  onLoad(options) {{
    if (options.id) {{
      this.setData({{ userId: options.id }})
      this.loadUserData(options.id)
    }}
  }},

  async loadUserData(userId) {{
    try {{
      const res = await wx.request({{
        url: app.globalData.baseUrl + `/api/users/${{userId}}`
      }})

      if (res.data.success) {{
        this.setData({{
          inviteCount: res.data.data.invite_count || 0,
          inviteList: res.data.data.invites || []
        }})
      }}
    }} catch (err) {{
      console.error('加载数据失败', err)
    }}
  }},

  // 分享给好友
  onShareAppMessage() {{
    return {{
      title: '我领到了优惠券，你也来领一个吧！',
      path: `/pages/index/index?pid=${{this.data.userId}}`,
      imageUrl: '/images/share.png'
    }}
  }},

  // 分享到朋友圈
  onShareTimeline() {{
    return {{
      title: '限时优惠券，快来领取！',
      query: `pid=${{this.data.userId}}`
    }}
  }},

  // 生成海报
  generatePoster() {{
    wx.showToast({{ title: '海报生成中...', icon: 'loading' }})
    // TODO: 实现海报生成逻辑
  }}
}})
"""

        return {"wxml": wxml, "wxss": wxss, "js": js}

    # ------------------------------------------------------------------ #
    #  基础页面
    # ------------------------------------------------------------------ #

    def _generate_basic_page(self, page_name: str) -> Dict[str, str]:
        """生成最简基础页面"""
        wxml = f'<!--{page_name}.wxml-->\n<view class="container">\n  <text>{{{{message}}}}</text>\n</view>'
        wxss = f'/* {page_name}.wxss */\n.container {{ padding: 30rpx; }}'
        js = f'// {page_name}.js\nPage({{\n  data: {{ message: "Hello" }}\n}})'
        return {"wxml": wxml, "wxss": wxss, "js": js}

    # ------------------------------------------------------------------ #
    #  页面 JSON 配置
    # ------------------------------------------------------------------ #

    def _generate_json(self, page_name: str, features: List[str]) -> str:
        """生成页面 JSON 配置"""
        config: Dict[str, Any] = {
            "navigationBarTitleText": page_name.capitalize(),
            "usingComponents": {},
        }

        if "下拉刷新" in features or "pulldown" in features:
            config["enablePullDownRefresh"] = True

        if "分享" in features or "share" in features:
            config["navigationBarTitleText"] = "分享"

        return json.dumps(config, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------ #
    #  文件保存
    # ------------------------------------------------------------------ #

    def save_files(self, page_name: str, results: Dict[str, str]) -> Dict[str, Path]:
        """将生成的页面代码保存到文件

        Args:
            page_name: 页面名称
            results: generate() 返回的代码字典

        Returns:
            {文件类型: 文件路径} 的字典
        """
        page_dir = self.output_dir / "pages" / page_name
        page_dir.mkdir(parents=True, exist_ok=True)

        saved: Dict[str, Path] = {}
        for ext, content in results.items():
            file_path = page_dir / f"{page_name}.{ext}"
            file_path.write_text(content, encoding="utf-8")
            saved[ext] = file_path

        return saved


__all__ = ["MiniprogramPageGenerator"]
