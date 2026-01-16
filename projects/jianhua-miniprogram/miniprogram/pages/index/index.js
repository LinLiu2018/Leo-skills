// pages/index/index.js
const app = getApp();

Page({
  data: {
    isLogin: false,
    userInfo: null,
    totalClaimed: 386,
    // 视频URL - 替换为实际视频地址
    videoUrl: '',
    videoPoster: '',
    // 图片列表 - 替换为实际图片地址
    galleryImages: [
      'https://placeholder.com/image1.jpg',
      'https://placeholder.com/image2.jpg',
      'https://placeholder.com/image3.jpg',
      'https://placeholder.com/image4.jpg'
    ],
    giftList: [
      { level: 1, name: '抽纸', emoji: '🧻', condition: '0人' },
      { level: 2, name: '洗衣液', emoji: '🧴', condition: '3人' },
      { level: 3, name: '大米', emoji: '🍚', condition: '10人' },
      { level: 4, name: '食用油', emoji: '🫒', condition: '20人' }
    ],
    dynamics: [
      { name: '张*芳', gift: '抽纸1包', time: '刚刚' },
      { name: '李*明', gift: '洗衣液1瓶', time: '2分钟前' },
      { name: '王*华', gift: '抽纸1包', time: '5分钟前' },
      { name: '赵*强', gift: '大米5斤', time: '8分钟前' }
    ]
  },

  onLoad(options) {
    if (options.invite) {
      app.globalData.inviteCode = options.invite;
      wx.setStorageSync('inviteCode', options.invite);
    }
    this.checkLoginStatus();
  },

  onShow() {
    this.checkLoginStatus();
  },

  checkLoginStatus() {
    const isLogin = app.globalData.isLogin;
    const userInfo = app.globalData.userInfo;
    this.setData({ isLogin, userInfo });
  },

  onGetPhone(e) {
    if (e.detail.code) {
      wx.showLoading({ title: '领取中...' });

      app.phoneLogin(e.detail.code).then(res => {
        wx.hideLoading();

        if (res.success) {
          this.setData({ isLogin: true, userInfo: res.user });

          wx.showModal({
            title: '🎉 领取成功',
            content: res.message,
            confirmText: '去分享',
            cancelText: '稍后再说',
            success: (result) => {
              if (result.confirm) {
                wx.switchTab({ url: '/pages/share/share' });
              }
            }
          });
        }
      }).catch(() => {
        wx.hideLoading();
        wx.showToast({ title: '领取失败，请重试', icon: 'none' });
      });
    } else {
      wx.showToast({ title: '需要授权手机号才能领取', icon: 'none' });
    }
  },

  callTong() {
    wx.makePhoneCall({ phoneNumber: '17855076342' });
  },

  callLiu() {
    wx.makePhoneCall({ phoneNumber: '18601764990' });
  },

  previewImage(e) {
    const src = e.currentTarget.dataset.src;
    wx.previewImage({
      current: src,
      urls: this.data.galleryImages
    });
  },

  onShareAppMessage() {
    const inviteCode = this.data.userInfo?.invite_code || '';
    return {
      title: '🎁 免费领取精美礼品，快来参与！',
      path: `/pages/index/index?invite=${inviteCode}`
    };
  }
});
