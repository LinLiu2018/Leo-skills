const app = getApp()

Page({
  data: {
    loading: false,
    pid: ''
  },

  onLoad(options) {
    // 获取分享人ID
    this.setData({
      pid: options.pid || ''
    })
  },

  // 处理授权
  async handleAuth() {
    this.setData({ loading: true })

    try {
      // 1. 获取用户信息授权
      const userInfo = await this.getUserInfo()

      // 2. 登录获取code
      const loginRes = await wx.login()
      if (!loginRes.code) {
        throw new Error('登录失败')
      }

      // 3. 提交到后端
      const result = await this.submitToServer(loginRes.code, userInfo)

      if (result.success) {
        // 跳转到优惠券页面
        wx.redirectTo({
          url: `/pages/coupon/coupon?uid=${result.user_id}`
        })
      } else {
        wx.showToast({
          title: result.message || '提交失败',
          icon: 'none'
        })
      }
    } catch (error) {
      wx.showToast({
        title: error.message || '授权失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 获取用户信息
  getUserInfo() {
    return new Promise((resolve, reject) => {
      wx.getUserProfile({
        desc: '用于领取优惠券',
        success: (res) => {
          resolve(res.userInfo)
        },
        fail: (err) => {
          reject(new Error('请授权获取用户信息'))
        }
      })
    })
  },

  // 提交到服务器
  submitToServer(code, userInfo) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.apiUrl}/miniprogram/submit`,
        method: 'POST',
        data: {
          code: code,
          nickname: userInfo.nickName,
          avatar: userInfo.avatarUrl,
          pid: this.data.pid
        },
        success: (res) => {
          resolve(res.data)
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '建华官园菜场开业大酬宾，快来领优惠券！',
      path: `/pages/index/index?pid=${wx.getStorageSync('userId') || ''}`
    }
  }
})
