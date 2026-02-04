// app.js
App({
  globalData: {
    userInfo: null,
    isLogin: false,
    inviteCode: '', // 邀请码（从URL参数获取）
    baseUrl: 'http://localhost:3000/api/v1', // 后端API地址
    mockMode: true // 开发模式：使用模拟数据
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
      // 模拟模式：直接返回模拟数据
      if (this.globalData.mockMode) {
        console.log('[Mock] 模拟登录成功');
        const mockUser = {
          id: 'mock_user_001',
          nickname: '测试用户',
          avatar: '',
          phone: '138****8888',
          inviteCode: 'MOCK001',
          inviteCount: 5,
          createdAt: new Date().toISOString()
        };
        const mockToken = 'mock_token_' + Date.now();

        this.globalData.isLogin = true;
        this.globalData.userInfo = mockUser;
        wx.setStorageSync('token', mockToken);
        wx.setStorageSync('userInfo', mockUser);

        setTimeout(() => {
          resolve({
            success: true,
            user: mockUser,
            token: mockToken
          });
        }, 500); // 模拟网络延迟
        return;
      }

      // 真实API调用
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
