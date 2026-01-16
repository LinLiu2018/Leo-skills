// app.js
App({
  globalData: {
    userInfo: null,
    isLogin: false,
    inviteCode: '', // 邀请码（从URL参数获取）
    baseUrl: 'http://localhost:3000/api/v1' // 后端API地址
  },

  onLaunch(options) {
    // 获取邀请码
    if (options.query && options.query.invite) {
      this.globalData.inviteCode = options.query.invite;
      wx.setStorageSync('inviteCode', options.query.invite);
    }

    // 检查登录状态
    const token = wx.getStorageSync('token');
    if (token) {
      this.globalData.isLogin = true;
      this.globalData.userInfo = wx.getStorageSync('userInfo');
    }
  },

  // 一键手机授权登录
  phoneLogin(code) {
    return new Promise((resolve, reject) => {
      const inviteCode = this.globalData.inviteCode || wx.getStorageSync('inviteCode');

      // Mock数据 - 实际开发时替换为真实API
      setTimeout(() => {
        const mockResponse = {
          success: true,
          user: {
            id: 123,
            phone: '138****8000',
            nickname: '微信用户',
            avatar: '/images/default-avatar.png',
            invite_code: 'ABC123',
            is_new_user: true,
            initial_gift: {
              name: '抽纸1包',
              code: 'GIFT001',
              expire_at: '2026-01-22'
            }
          },
          token: 'mock_jwt_token',
          message: '恭喜获得抽纸1包，快分享给好友解锁更多礼品吧！'
        };

        this.globalData.isLogin = true;
        this.globalData.userInfo = mockResponse.user;
        wx.setStorageSync('token', mockResponse.token);
        wx.setStorageSync('userInfo', mockResponse.user);

        resolve(mockResponse);
      }, 500);
    });
  }
});
