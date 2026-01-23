// pages/index/index.js
const app = getApp();

Page({
  data: {
    isLogin: false,
    userInfo: null,
    totalClaimed: 386,
    // 视频URL - 替换为实际视频地址
    videoUrl: 'https://wxsnsdy.tc.qq.com/105/20210/snsdyvideodownload?filekey=30280201010421301f0201690402534804102ca905ce620b1241b726bc41dcff44e00204012882540400&bizid=1023&hy=SH&fileparam=302c020101042530230204136ffd93020457e3c4ff02024ef202031e8d7f02030f42400204045a320a0201000400',
    videoPoster: '',
    // 图片列表 - 替换为实际图片地址
    galleryImages: [
      'https://res.wx.qq.com/wxdoc/dist/assets/img/0.4cb08bb4.jpg',
      'https://res.wx.qq.com/wxdoc/dist/assets/img/0.4cb08bb4.jpg',
      'https://res.wx.qq.com/wxdoc/dist/assets/img/0.4cb08bb4.jpg'
    ],
    giftList: [
      { level: 1, name: '抽纸', condition: '0人' },
      { level: 2, name: '洗衣液', condition: '3人' },
      { level: 3, name: '大米', condition: '10人' },
      { level: 4, name: '食用油', condition: '20人' },
      { level: 6, name: '100元卡', condition: '30人' },
      { level: 5, name: '神秘大奖', condition: '50人' }
    ],
    dynamics: [
      { name: '张*芳', gift: '抽纸1包', time: '刚刚' },
      { name: '李*明', gift: '洗衣液1瓶', time: '2分钟前' },
      { name: '王*华', gift: '抽纸1包', time: '5分钟前' },
      { name: '赵*强', gift: '大米5斤', time: '8分钟前' }
    ],
    contacts: [
      { name: '童经理', phone: '17855076342' },
      { name: '刘经理', phone: '18601764990' }
    ],
    challengeTime: '',
    timer: null
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
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 });
    }
  },

  onUnload() {
    if (this.data.timer) {
      clearInterval(this.data.timer);
    }
  },

  checkLoginStatus() {
    const isLogin = app.globalData.isLogin;
    const userInfo = app.globalData.userInfo;
    this.setData({ isLogin, userInfo });

    if (isLogin && userInfo && userInfo.created_at) {
      this.updateChallengeTimer();
    }
  },

  updateChallengeTimer() {
    const created = new Date(this.data.userInfo.created_at).getTime();
    const end = created + 24 * 60 * 60 * 1000;

    const tick = () => {
      const now = new Date().getTime();
      const diff = end - now;

      if (diff <= 0) {
        this.setData({ challengeTime: '已结束' });
        if (this.data.timer) clearInterval(this.data.timer);
        return;
      }

      const h = Math.floor(diff / (1000 * 60 * 60));
      const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const s = Math.floor((diff % (1000 * 60)) / 1000);

      const str = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
      this.setData({ challengeTime: str });
    };

    tick();
    const timer = setInterval(tick, 1000);
    this.setData({ timer });
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

  callContact(e) {
    const phone = e.currentTarget.dataset.phone;
    wx.makePhoneCall({ phoneNumber: phone });
  },

  previewImage(e) {
    const src = e.currentTarget.dataset.src;
    wx.previewImage({
      current: src,
      urls: this.data.galleryImages
    });
  },

  goToShare() {
    if (this.data.isLogin) {
      wx.switchTab({ url: '/pages/share/share' });
    } else {
      // Trigger login or scroll to login button (simplified: show toast)
      wx.showToast({ title: '请先领取礼品', icon: 'none' });
    }
  },

  onShareAppMessage() {
    const inviteCode = this.data.userInfo?.invite_code || '';
    return {
      title: '🎁 免费领取精美礼品，快来参与！',
      path: `/pages/index/index?invite=${inviteCode}`
    };
  }
});
