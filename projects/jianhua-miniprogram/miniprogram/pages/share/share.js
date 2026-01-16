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
      { level: 5, name: '神秘大奖', requireText: '邀请50人', status: 'locked', remaining: 38 }
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
    // Mock数据 - 实际开发时替换为API调用
    const stats = this.data.shareStats;
    const totalInvites = stats.total_invites;

    // 计算进度和下一个礼品
    let nextGift = { name: '神秘大奖', required: 50 };
    let progressPercent = 100;

    if (totalInvites < 3) {
      nextGift = { name: '洗衣液', required: 3 };
      progressPercent = (totalInvites / 3) * 100;
    } else if (totalInvites < 10) {
      nextGift = { name: '大米', required: 10 };
      progressPercent = (totalInvites / 10) * 100;
    } else if (totalInvites < 20) {
      nextGift = { name: '食用油', required: 20 };
      progressPercent = (totalInvites / 20) * 100;
    } else if (totalInvites < 50) {
      nextGift = { name: '神秘大奖', required: 50 };
      progressPercent = (totalInvites / 50) * 100;
    }

    // 更新礼品状态
    const giftList = this.data.giftList.map(gift => {
      const thresholds = [0, 3, 10, 20, 50];
      const threshold = thresholds[gift.level - 1];

      if (gift.level <= 2) {
        // 假设前两个已领取
        gift.status = 'claimed';
        gift.remaining = 0;
      } else if (totalInvites >= threshold) {
        gift.status = 'unlocked';
        gift.remaining = 0;
      } else {
        gift.status = 'locked';
        gift.remaining = threshold - totalInvites;
      }
      return gift;
    });

    this.setData({
      nextGift,
      progressPercent,
      giftList
    });
  },

  // 领取礼品
  claimGift(e) {
    const level = e.currentTarget.dataset.level;
    const gift = this.data.giftList.find(g => g.level === level);

    wx.showModal({
      title: '领取礼品',
      content: `确定领取「${gift.name}」吗？领取后需要预约到访核销。`,
      confirmText: '确定领取',
      success: (res) => {
        if (res.confirm) {
          // 跳转到预约页面
          wx.navigateTo({
            url: `/pages/appointment/appointment?giftLevel=${level}&giftName=${gift.name}`
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
