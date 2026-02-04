// pages/index/index.js
const app = getApp();
const mockApi = require('../../utils/mockApi');

Page({
  data: {
    isLogin: false,
    userInfo: null,
    inviteCount: 0,
    totalClaimed: 386,
    videoUrl: 'https://wxsnsdy.tc.qq.com/105/20210/snsdyvideodownload?filekey=30280201010421301f0201690402534804102ca905ce620b1241b726bc41dcff44e00204012882540400&bizid=1023&hy=SH&fileparam=302c020101042530230204136ffd93020457e3c4ff02024ef202031e8d7f02030f42400204045a320a0201000400',
    videoPoster: '',
    galleryImages: [
      'https://res.wx.qq.com/wxdoc/dist/assets/img/0.4cb08bb4.jpg',
      'https://res.wx.qq.com/wxdoc/dist/assets/img/0.4cb08bb4.jpg',
      'https://res.wx.qq.com/wxdoc/dist/assets/img/0.4cb08bb4.jpg'
    ],
    giftList: [],
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
    timer: null,
    pendingInviteCode: ''
  },

  onLoad(options) {
    // 处理分享带来的邀请码
    const inviteCode = options.invite || options.inviteCode || '';
    if (inviteCode) {
      this.setData({ pendingInviteCode: inviteCode });
      wx.setStorageSync('pendingInviteCode', inviteCode);
    }
    this.checkLoginStatus();
    this.loadGiftList();
  },

  onShow() {
    this.checkLoginStatus();
    this.loadGiftList();
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 });
    }
  },

  onUnload() {
    if (this.data.timer) clearInterval(this.data.timer);
  },

  async checkLoginStatus() {
    const user = mockApi.getCurrentUser();
    if (user) {
      const res = await mockApi.getUserInfo();
      if (res.success) {
        this.setData({
          isLogin: true,
          userInfo: res.data,
          inviteCount: res.data.inviteCount || 0
        });
        app.globalData.isLogin = true;
        app.globalData.userInfo = res.data;
        this.updateChallengeTimer();
      }
    } else {
      this.setData({ isLogin: false, userInfo: null, inviteCount: 0 });
    }
  },

  async loadGiftList() {
    const res = await mockApi.getGiftList();
    if (res.success) {
      const giftList = res.data.map(g => ({
        id: g.id,
        level: g.id.replace('gift_', ''),
        name: g.name,
        condition: `${g.requiredInvites}人`,
        status: g.status,
        progress: g.progress
      }));
      this.setData({ giftList });
    }
  },

  updateChallengeTimer() {
    const user = this.data.userInfo;
    if (!user || !user.createdAt) return;

    const created = new Date(user.createdAt).getTime();
    const end = created + 24 * 60 * 60 * 1000;

    const tick = () => {
      const now = Date.now();
      const diff = end - now;
      if (diff <= 0) {
        this.setData({ challengeTime: '已结束' });
        if (this.data.timer) clearInterval(this.data.timer);
        return;
      }
      const h = Math.floor(diff / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      this.setData({
        challengeTime: `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`
      });
    };

    tick();
    this.setData({ timer: setInterval(tick, 1000) });
  },

  async onGetPhone(e) {
    if (!e.detail.code) {
      wx.showToast({ title: '需要授权手机号才能领取', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '领取中...' });
    try {
      const res = await mockApi.phoneLogin(e.detail.code);
      wx.hideLoading();

      if (res.success) {
        // 处理待绑定的邀请码
        const pendingCode = this.data.pendingInviteCode || wx.getStorageSync('pendingInviteCode');
        if (pendingCode) {
          await mockApi.bindInvite(pendingCode);
          wx.removeStorageSync('pendingInviteCode');
        }

        this.setData({
          isLogin: true,
          userInfo: res.data,
          pendingInviteCode: ''
        });
        app.globalData.isLogin = true;
        app.globalData.userInfo = res.data;

        wx.showModal({
          title: '领取成功',
          content: '恭喜获得基础礼包！分享给好友可解锁更多礼品',
          confirmText: '去分享',
          cancelText: '稍后再说',
          success: (result) => {
            if (result.confirm) {
              wx.switchTab({ url: '/pages/share/share' });
            }
          }
        });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '领取失败，请重试', icon: 'none' });
    }
  },

  goToGiftDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/gift-detail/gift-detail?id=${id}` });
  },

  callContact(e) {
    wx.makePhoneCall({ phoneNumber: e.currentTarget.dataset.phone });
  },

  previewImage(e) {
    wx.previewImage({
      current: e.currentTarget.dataset.src,
      urls: this.data.galleryImages
    });
  },

  goToShare() {
    if (this.data.isLogin) {
      wx.switchTab({ url: '/pages/share/share' });
    } else {
      wx.showToast({ title: '请先领取礼品', icon: 'none' });
    }
  },

  // 测试用：模拟新增邀请
  async testAddInvite() {
    if (!this.data.isLogin) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    await mockApi.simulateNewInvite();
    await this.checkLoginStatus();
    await this.loadGiftList();
    wx.showToast({ title: '模拟邀请成功', icon: 'success' });
  },

  onShareAppMessage() {
    const user = this.data.userInfo;
    const inviteCode = user ? user.inviteCode : '';
    return {
      title: '免费领取精美礼品，快来参与！',
      path: `/pages/index/index?inviteCode=${inviteCode}`,
      imageUrl: ''
    };
  },

  // 礼品图片加载失败时使用占位图
  onGiftImageError(e) {
    const index = e.currentTarget.dataset.index;
    const giftList = this.data.giftList;
    if (giftList[index]) {
      // 使用真实的礼品图片
      const imageUrls = [
        'https://minimax-algeng-chat-tts.oss-cn-wulanchabu.aliyuncs.com/ccv2%2F2026-01-29%2FMiniMax-M2.1%2F2007435025913487546%2Fcc93a2a28346b24744c11b2d530e966b186ef4ebfbe7050b01bcdd510eb40870..png?Expires=1769744971&OSSAccessKeyId=LTAI5tGLnRTkBjLuYPjNcKQ8&Signature=NNWXQq3CpvkHRFSThimooVZQfuI%3D',
        'https://minimax-algeng-chat-tts.oss-cn-wulanchabu.aliyuncs.com/ccv2%2F2026-01-29%2FMiniMax-M2.1%2F2007435025913487546%2Fcc93a2a28346b24744c11b2d530e966b186ef4ebfbe7050b01bcdd510eb40870..png?Expires=1769744971&OSSAccessKeyId=LTAI5tGLnRTkBjLuYPjNcKQ8&Signature=NNWXQq3CpvkHRFSThimooVZQfuI%3D',
        'https://minimax-algeng-chat-tts.oss-cn-wulanchabu.aliyuncs.com/ccv2%2F2026-01-29%2FMiniMax-M2.1%2F2007435025913487546%2Fcc93a2a28346b24744c11b2d530e966b186ef4ebfbe7050b01bcdd510eb40870..png?Expires=1769744971&OSSAccessKeyId=LTAI5tGLnRTkBjLuYPjNcKQ8&Signature=NNWXQq3CpvkHRFSThimooVZQfuI%3D',
        'https://minimax-algeng-chat-tts.oss-cn-wulanchabu.aliyuncs.com/ccv2%2F2026-01-29%2FMiniMax-M2.1%2F2007435025913487546%2Fcc93a2a28346b24744c11b2d530e966b186ef4ebfbe7050b01bcdd510eb40870..png?Expires=1769744971&OSSAccessKeyId=LTAI5tGLnRTkBjLuYPjNcKQ8&Signature=NNWXQq3CpvkHRFSThimooVZQfuI%3D'
      ];
      giftList[index].imageUrl = imageUrls[index % imageUrls.length];
      this.setData({ giftList });
    }
  }
});