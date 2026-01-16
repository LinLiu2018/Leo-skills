// pages/user/user.js
const app = getApp();

Page({
  data: {
    isLogin: false,
    userInfo: {},
    stats: {
      inviteCount: 0,
      giftCount: 0,
      visitCount: 0
    },
    gifts: []
  },

  onLoad() {
    this.checkLogin();
  },

  onShow() {
    this.checkLogin();
  },

  checkLogin() {
    const isLogin = app.globalData.isLogin;
    const userInfo = app.globalData.userInfo || {};

    this.setData({ isLogin, userInfo });

    if (isLogin) {
      this.loadUserData();
    }
  },

  loadUserData() {
    // Mock数据
    this.setData({
      stats: {
        inviteCount: 3,
        giftCount: 2,
        visitCount: 0
      },
      gifts: [
        { id: 1, name: '抽纸1包', status: 'pending', statusText: '待领取', expire: '有效期至1月22日' },
        { id: 2, name: '洗衣液1瓶', status: 'claimed', statusText: '已领取', expire: '1月10日领取' }
      ]
    });
  },

  onGetPhone(e) {
    if (e.detail.code) {
      wx.showLoading({ title: '登录中...' });

      app.phoneLogin(e.detail.code).then(res => {
        wx.hideLoading();
        if (res.success) {
          this.checkLogin();
          wx.showToast({ title: '登录成功', icon: 'success' });
        }
      }).catch(() => {
        wx.hideLoading();
        wx.showToast({ title: '登录失败', icon: 'none' });
      });
    }
  },

  goToAppointment() {
    wx.navigateTo({ url: '/pages/appointment/appointment' });
  },

  goToShare() {
    wx.switchTab({ url: '/pages/share/share' });
  },

  makePhoneCall() {
    wx.makePhoneCall({ phoneNumber: '400-888-8888' });
  },

  showAbout() {
    wx.showModal({
      title: '关于我们',
      content: '建华观园菜场\n淮安市清江浦区\n优质商铺 投资首选',
      showCancel: false
    });
  },

  viewAllGifts() {
    wx.showToast({ title: '功能开发中', icon: 'none' });
  },

  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          app.globalData.isLogin = false;
          app.globalData.userInfo = null;
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');

          this.setData({
            isLogin: false,
            userInfo: {},
            stats: { inviteCount: 0, giftCount: 0, visitCount: 0 },
            gifts: []
          });

          wx.showToast({ title: '已退出', icon: 'success' });
        }
      }
    });
  }
});
