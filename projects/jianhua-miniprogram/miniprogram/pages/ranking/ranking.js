// pages/ranking/ranking.js
const app = getApp()
const mockApi = require('../../utils/mockApi')

Page({
  data: {
    isLogin: false,
    userInfo: {},
    loading: true,
    rankList: [],
    myRank: null,
    myInviteCount: 0
  },

  onLoad() {
    this.checkLogin()
    this.loadRankList()
  },

  onShow() {
    this.checkLogin()
    this.loadRankList()
  },

  checkLogin() {
    const user = mockApi.getCurrentUser()
    this.setData({
      isLogin: !!user,
      userInfo: user || {}
    })
  },

  async loadRankList() {
    this.setData({ loading: true })

    try {
      const res = await mockApi.getRanking()
      if (res.success) {
        this.setData({
          rankList: res.data.list.map(item => ({
            id: item.id,
            nickname: item.nickname,
            avatar: item.avatar,
            invite_count: item.inviteCount,
            isMe: item.isMe
          })),
          myRank: res.data.myRank,
          myInviteCount: res.data.myInviteCount,
          loading: false
        })
      }
    } catch (err) {
      console.error('加载排行榜失败:', err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  onPullDownRefresh() {
    this.loadRankList().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onShareAppMessage() {
    const user = mockApi.getCurrentUser()
    const inviteCode = user ? user.inviteCode : ''
    return {
      title: '快来看看谁是邀请王！',
      path: `/pages/index/index?inviteCode=${inviteCode}`
    }
  }
})
