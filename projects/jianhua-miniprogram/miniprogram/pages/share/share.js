// pages/share/share.js
const app = getApp();

Page({
  data: {
    isLogin: false,
    userInfo: null,
    shareStats: {
      total_invites: 12,
      today_invites: 3,
      total_shares: 25
    },
    progressPercent: 60,
    nextGift: { name: '食用油', required: 20 },
    giftList: [
      { level: 1, name: '抽纸1包', requireText: '授权即领', status: 'claimed', remaining: 0 },
      { level: 2, name: '洗衣液1瓶', requireText: '邀请3人', status: 'claimed', remaining: 0 },
      { level: 3, name: '大米5斤', requireText: '邀请10人', status: 'unlocked', remaining: 0 },
      { level: 4, name: '食用油1桶', requireText: '邀请20人', status: 'locked', remaining: 8 },
      { level: 5, name: '100元超市卡', requireText: '邀请30人', status: 'locked', remaining: 18 },
      { level: 6, name: '神秘大奖', requireText: '邀请50人', status: 'locked', remaining: 38 }
    ],
    inviteeList: [
      { id: 1, nickname: '张**', phone: '138****1234', avatar: '', created_at: '今天 10:32' },
      { id: 2, nickname: '李**', phone: '159****5678', avatar: '', created_at: '今天 09:15' },
      { id: 3, nickname: '王**', phone: '186****9012', avatar: '', created_at: '昨天 18:45' }
    ]
  },

  onLoad() {
    this.checkLoginStatus();
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 });
    }
    this.checkLoginStatus();
    if (app.globalData.isLogin) {
      this.loadShareStats();
    }
  },

  checkLoginStatus() {
    const isLogin = app.globalData.isLogin;
    const userInfo = app.globalData.userInfo;
    this.setData({ isLogin, userInfo });
  },

  // 加载分享统计数据
  loadShareStats() {
    const token = wx.getStorageSync('token');
    if (!token) return;

    wx.request({
      url: `${app.globalData.baseUrl}/gift/progress`,
      method: 'GET',
      header: { Authorization: `Bearer ${token}` },
      success: (res) => {
        if (res.data.success) {
          const { inviteCount, gifts, nextTarget, progress } = res.data;

          // Map API gifts to view model
          const giftList = gifts.map((g, index) => ({
            level: index + 1, // Use index as level for display order
            giftId: g.id, // Keep real ID for claiming
            name: g.name,
            required: g.required,
            requireText: g.required === 0 ? '授权即领' : `邀请${g.required}人`,
            status: g.claimed ? 'claimed' : (g.unlocked ? 'unlocked' : 'locked'),
            remaining: Math.max(0, g.required - inviteCount)
          }));

          // Find next target gift name
          let nextGiftName = '神秘大奖';
          const nextTargetGift = gifts.find(g => g.required === nextTarget);
          if (nextTargetGift) {
            nextGiftName = nextTargetGift.name;
          }

          this.setData({
            shareStats: {
              total_invites: inviteCount,
              today_invites: 0, // API doesn't return this yet, keep 0 or add to API
              total_shares: 0   // API doesn't return this yet
            },
            nextGift: { name: nextGiftName, required: nextTarget || 50 },
            progressPercent: progress,
            giftList,
            inviteeList: [] // Clear mock data until API is ready
          });
        }
      },
      fail: (err) => {
        console.error('Fetch progress failed:', err);
      }
    });
  },

  // 领取礼品
  claimGift(e) {
    const index = e.currentTarget.dataset.index; // Use index or get object
    // Or better, look up in giftList
    const level = e.currentTarget.dataset.level;
    const gift = this.data.giftList.find(g => g.level === level);

    if (!gift) return;
    if (gift.status === 'locked') {
      wx.showToast({ title: `还需要邀请${gift.remaining}人`, icon: 'none' });
      return;
    }
    if (gift.status === 'claimed') {
      wx.navigateTo({
        url: `/pages/appointment/appointment?giftId=${gift.giftId}&giftName=${gift.name}`
      });
      return;
    }

    wx.showModal({
      title: '领取礼品',
      content: `确定领取「${gift.name}」吗？领取后需要预约到访核销。`,
      confirmText: '确定领取',
      success: (res) => {
        if (res.confirm) {
           const token = wx.getStorageSync('token');
           wx.showLoading({ title: '处理中' });

           wx.request({
             url: `${app.globalData.baseUrl}/gift/claim`,
             method: 'POST',
             header: { Authorization: `Bearer ${token}` },
             data: { giftId: gift.giftId },
             success: (res) => {
               wx.hideLoading();
               if (res.data.success) {
                  wx.showToast({ title: '领取成功', icon: 'success' });
                  this.loadShareStats(); // Reload to update status

                  setTimeout(() => {
                    wx.navigateTo({
                      url: `/pages/appointment/appointment?giftId=${gift.giftId}&giftName=${gift.name}`
                    });
                  }, 1500);
               } else {
                 wx.showToast({ title: res.data.message || '领取失败', icon: 'none' });
               }
             },
             fail: () => {
               wx.hideLoading();
               wx.showToast({ title: '网络错误', icon: 'none' });
             }
           });
        }
      }
    });
  },

  // 跳转首页
  goToIndex() {
    wx.switchTab({ url: '/pages/index/index' });
  },

  // 分享配置
  onShareAppMessage() {
    const inviteCode = this.data.userInfo?.invite_code || '';
    return {
      title: '🎁 我已领取精美礼品，你也来试试！',
      path: `/pages/index/index?invite=${inviteCode}`,
      imageUrl: '/images/share-cover.png'
    };
  }
});
