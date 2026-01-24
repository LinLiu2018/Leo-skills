// invites.js
const app = getApp()

Page({
  data: {
    list: [],
    loading: false,
    page: 1,
    hasMore: true
  },

  onLoad() {
    this.loadData()
  },

  onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true })
    this.loadData().then(() => wx.stopPullDownRefresh())
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadData()
    }
  },

  async loadData() {
    this.setData({ loading: true })

    try {
      const res = await wx.request({
        url: app.globalData.baseUrl + '/api/leads',
        data: { page: this.data.page }
      })

      if (res.data.success) {
        const newList = this.data.page === 1 ? res.data.data : [...this.data.list, ...res.data.data]
        this.setData({
          list: newList,
          page: this.data.page + 1,
          hasMore: res.data.data.length > 0
        })
      }
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  onItemTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  }
})
