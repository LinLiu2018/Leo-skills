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

      wx.request({
        url: `${this.globalData.baseUrl}/auth/phone-login`,
        method: 'POST',
        data: {
          code: code,
          inviteCode: inviteCode
        },
        success: (res) => {
          if (res.data.success) {
            const user = res.data.user;
            const token = res.data.token;

            this.globalData.isLogin = true;
            this.globalData.userInfo = user;
            wx.setStorageSync('token', token);
            wx.setStorageSync('userInfo', user);

            resolve(res.data);
          } else {
            console.error('Login failed:', res.data.message);
            reject(res.data.message);
          }
        },
        fail: (err) => {
          console.error('Request failed:', err);
          reject(err);
        }
      });
    });
  }
});
