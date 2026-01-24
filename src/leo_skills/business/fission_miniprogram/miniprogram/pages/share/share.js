// share.js
const app = getApp()

Page({
  data: {
    couponValue: 10,
    inviteCount: 0,
    inviteList: [],
    userId: null
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ userId: options.id })
      this.loadUserData(options.id)
    }
  },

  async loadUserData(userId) {
    try {
      const res = await wx.request({
        url: app.globalData.baseUrl + `/api/users/${userId}`
      })

      if (res.data.success) {
        this.setData({
          inviteCount: res.data.data.invite_count || 0,
          inviteList: res.data.data.invites || []
        })
      }
    } catch (err) {
      console.error('加载数据失败', err)
    }
  },

  // 分享给好友
  onShareAppMessage() {
    return {
      title: '我领到了优惠券，你也来领一个吧！',
      path: `/pages/index/index?pid=${this.data.userId}`,
      imageUrl: '/images/share.png'
    }
  },

  // 分享到朋友圈
  onShareTimeline() {
    return {
      title: '限时优惠券，快来领取！',
      query: `pid=${this.data.userId}`
    }
  },

  // 生成海报
  generatePoster() {
    wx.showToast({ title: '海报生成中...', icon: 'loading' })
    // TODO: 实现海报生成逻辑
  }
})
