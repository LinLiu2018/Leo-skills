// pages/share/share.js
const app = getApp();
const mockApi = require('../../utils/mockApi');

Page({
  data: {
    isLogin: false,
    userInfo: null,
    shareStats: {
      total_invites: 0,
      today_invites: 0
    },
    progressPercent: 0,
    nextGift: { name: '精美水果礼盒', required: 3 },
    giftList: [],
    inviteeList: []
  },

  onLoad() {
    this.checkLoginStatus();
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 });
    }
    this.checkLoginStatus();
    this.loadShareStats();
  },

  async checkLoginStatus() {
    const user = mockApi.getCurrentUser();
    if (user) {
      const res = await mockApi.getUserInfo();
      if (res.success) {
        this.setData({
          isLogin: true,
          userInfo: res.data
        });
        app.globalData.isLogin = true;
        app.globalData.userInfo = res.data;
      }
    } else {
      this.setData({ isLogin: false, userInfo: null });
    }
  },

  async loadShareStats() {
    const user = mockApi.getCurrentUser();
    if (!user) return;

    // 获取礼品列表
    const giftRes = await mockApi.getGiftList();
    const inviteRes = await mockApi.getMyInvites();

    if (giftRes.success) {
      const inviteCount = inviteRes.success ? inviteRes.data.total : 0;
      const giftList = giftRes.data.map((g, index) => ({
        level: index + 1,
        id: g.id,
        name: g.name,
        required: g.requiredInvites,
        requireText: g.requiredInvites === 0 ? '授权即领' : `邀请${g.requiredInvites}人`,
        status: g.status,
        remaining: Math.max(0, g.requiredInvites - inviteCount),
        progress: g.progress
      }));

      // 找到下一个目标礼品
      const nextGift = giftList.find(g => g.status === 'locked') || giftList[giftList.length - 1];
      const progressPercent = nextGift ? Math.min(100, Math.round((inviteCount / nextGift.required) * 100)) : 100;

      this.setData({
        shareStats: { total_invites: inviteCount, today_invites: 0 },
        nextGift: { name: nextGift?.name || '全部完成', required: nextGift?.required || 0 },
        progressPercent,
        giftList,
        inviteeList: inviteRes.success ? inviteRes.data.list.map(i => ({
          id: i.id,
          nickname: i.inviteeName,
          created_at: i.createdAt
        })) : []
      });
    }
  },

  goToGiftDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/gift-detail/gift-detail?id=${id}` });
  },

  async claimGift(e) {
    const id = e.currentTarget.dataset.id;
    const gift = this.data.giftList.find(g => g.id === id);
    if (!gift) return;

    if (gift.status === 'locked') {
      wx.showToast({ title: `还需邀请${gift.remaining}人`, icon: 'none' });
      return;
    }
    if (gift.status === 'claimed') {
      wx.navigateTo({ url: `/pages/gift-detail/gift-detail?id=${id}` });
      return;
    }

    wx.showModal({
      title: '领取礼品',
      content: `确定领取「${gift.name}」吗？`,
      confirmText: '确定领取',
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '处理中' });
          const result = await mockApi.claimGift(id);
          wx.hideLoading();

          if (result.success) {
            wx.showToast({ title: '领取成功', icon: 'success' });
            this.loadShareStats();
            setTimeout(() => {
              wx.navigateTo({ url: `/pages/gift-detail/gift-detail?id=${id}` });
            }, 1500);
          } else {
            wx.showToast({ title: result.message || '领取失败', icon: 'none' });
          }
        }
      }
    });
  },

  async testAddInvite() {
    await mockApi.simulateNewInvite();
    await this.loadShareStats();
    wx.showToast({ title: '模拟邀请成功', icon: 'success' });
  },

  goToIndex() {
    wx.switchTab({ url: '/pages/index/index' });
  },

  onShareAppMessage() {
    const user = this.data.userInfo;
    const inviteCode = user ? user.inviteCode : '';
    return {
      title: '我已领取精美礼品，你也来试试！',
      path: `/pages/index/index?inviteCode=${inviteCode}`,
      imageUrl: ''
    };
  }
});
