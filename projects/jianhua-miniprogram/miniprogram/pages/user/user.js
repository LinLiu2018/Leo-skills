// pages/user/user.js
const app = getApp();
const mockApi = require('../../utils/mockApi');

Page({
  data: {
    isLogin: false,
    userInfo: {},
    stats: {
      inviteCount: 0,
      giftCount: 0
    },
    gifts: []
  },

  onLoad() {
    this.checkLogin();
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 2 });
    }
    this.checkLogin();
  },

  async checkLogin() {
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
        this.loadUserData();
      }
    } else {
      this.setData({
        isLogin: false,
        userInfo: {},
        stats: { inviteCount: 0, giftCount: 0 },
        gifts: []
      });
    }
  },

  async loadUserData() {
    const [inviteRes, giftRes] = await Promise.all([
      mockApi.getMyInvites(),
      mockApi.getMyGifts()
    ]);

    const inviteCount = inviteRes.success ? inviteRes.data.total : 0;
    const gifts = giftRes.success ? giftRes.data.map(g => ({
      id: g.id,
      name: g.giftName,
      status: g.status === 'unused' ? 'pending' : 'used',
      statusText: g.status === 'unused' ? '待核销' : '已使用',
      code: g.code,
      expire: `有效期至 ${g.expireAt}`
    })) : [];

    this.setData({
      stats: {
        inviteCount,
        giftCount: gifts.length
      },
      gifts
    });
  },

  async onGetPhone(e) {
    if (!e.detail.code) {
      wx.showToast({ title: '需要授权手机号', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '登录中...' });
    try {
      const res = await mockApi.phoneLogin(e.detail.code);
      wx.hideLoading();
      if (res.success) {
        this.checkLogin();
        wx.showToast({ title: '登录成功', icon: 'success' });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '登录失败', icon: 'none' });
    }
  },

  goToGiftDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/gift-detail/gift-detail?id=${id}` });
  },

  goToShare() {
    wx.switchTab({ url: '/pages/share/share' });
  },

  makePhoneCall() {
    wx.makePhoneCall({ phoneNumber: '17855076342' });
  },

  showAbout() {
    wx.showModal({
      title: '关于我们',
      content: '建华观园菜场\n淮安市清江浦区\n优质商铺 投资首选',
      showCancel: false
    });
  },

  viewAllGifts() {
    wx.switchTab({ url: '/pages/share/share' });
  },

  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          mockApi.resetAllData();
          app.globalData.isLogin = false;
          app.globalData.userInfo = null;

          this.setData({
            isLogin: false,
            userInfo: {},
            stats: { inviteCount: 0, giftCount: 0 },
            gifts: []
          });

          wx.showToast({ title: '已退出', icon: 'success' });
        }
      }
    });
  }
});
