// pages/gift-detail/gift-detail.js
const app = getApp()
const mockApi = require('../../utils/mockApi')

Page({
  data: {
    loading: true,
    gift: {},
    usageRules: [
      '礼品需到店核销，请出示小程序领取页面',
      '每人限领一次，不可转让',
      '礼品有效期内使用，过期作废',
      '最终解释权归活动主办方所有'
    ]
  },

  onLoad(options) {
    const { id, level } = options
    this.giftId = id || level || 'gift_001'
    this.loadGiftDetail(this.giftId)
  },

  onShow() {
    // 每次显示时刷新数据
    if (this.giftId) {
      this.loadGiftDetail(this.giftId)
    }
  },

  async loadGiftDetail(giftId) {
    this.setData({ loading: true })

    try {
      const res = await mockApi.getGiftDetail(giftId)
      if (res.success) {
        // 使用礼品自带的规则或默认规则
        const rules = res.data.rules || this.data.usageRules
        this.setData({
          gift: res.data,
          usageRules: rules,
          loading: false
        })
      } else {
        throw new Error(res.message)
      }
    } catch (err) {
      console.error('加载礼品详情失败:', err)
      this.setData({ loading: false })
      wx.showToast({ title: err.message || '加载失败', icon: 'none' })
    }
  },

  async claimGift() {
    wx.showLoading({ title: '领取中...' })

    try {
      const res = await mockApi.claimGift(this.giftId)
      wx.hideLoading()

      if (res.success) {
        // 刷新礼品详情
        await this.loadGiftDetail(this.giftId)
        wx.showToast({ title: '领取成功！', icon: 'success' })
      } else {
        wx.showToast({ title: res.message || '领取失败', icon: 'none' })
      }
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: '领取失败', icon: 'none' })
    }
  },

  copyCode() {
    const code = this.data.gift.code
    if (code) {
      wx.setClipboardData({
        data: code,
        success: () => {
          wx.showToast({ title: '已复制兑换码', icon: 'success' })
        }
      })
    }
  },

  onShareAppMessage() {
    const user = mockApi.getCurrentUser()
    const inviteCode = user ? user.inviteCode : ''
    return {
      title: `邀请你领取【${this.data.gift.name || '精美礼品'}】`,
      path: `/pages/index/index?inviteCode=${inviteCode}`,
      imageUrl: this.data.gift.image || ''
    }
  }
})
