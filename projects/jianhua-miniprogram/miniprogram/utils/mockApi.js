/**
 * Mock API 服务 - 裂变小程序模拟数据
 * 用于前端开发测试，无需后端服务
 */

// 模拟延迟
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms));

// 存储键名
const STORAGE_KEYS = {
  USER: 'mock_user',
  INVITES: 'mock_invites',
  GIFTS: 'mock_gifts',
  CLAIMED: 'mock_claimed'
};

// 初始化礼品数据
const DEFAULT_GIFTS = [
  {
    id: 'gift_001',
    name: '精美水果礼盒',
    description: '新鲜时令水果，产地直供，品质保证',
    image: '/images/gifts/fruit-box.png',
    requiredInvites: 3,
    stock: 100,
    rules: ['每人限领1份', '需到店核销', '有效期7天', '不可转让']
  },
  {
    id: 'gift_002',
    name: '优质蔬菜套餐',
    description: '当日新鲜蔬菜，绿色健康，营养丰富',
    image: '/images/gifts/veggie-pack.png',
    requiredInvites: 5,
    stock: 80,
    rules: ['每人限领1份', '需到店核销', '有效期5天', '不可转让']
  },
  {
    id: 'gift_003',
    name: '进口海鲜大礼包',
    description: '精选进口海鲜，新鲜冷链配送',
    image: '/images/gifts/seafood-pack.png',
    requiredInvites: 10,
    stock: 50,
    rules: ['每人限领1份', '需到店核销', '有效期3天', '冷藏保存']
  },
  {
    id: 'gift_004',
    name: '100元购物券',
    description: '全场通用，满200可用',
    image: '/images/gifts/coupon-100.png',
    requiredInvites: 8,
    stock: 200,
    rules: ['每人限领1张', '满200元可用', '有效期30天', '不可叠加']
  }
];

// 初始化排行榜数据
const DEFAULT_RANKING = [
  { id: 'user_001', nickname: '张大妈', avatar: '', inviteCount: 28, rank: 1 },
  { id: 'user_002', nickname: '李阿姨', avatar: '', inviteCount: 23, rank: 2 },
  { id: 'user_003', nickname: '王叔叔', avatar: '', inviteCount: 19, rank: 3 },
  { id: 'user_004', nickname: '赵姐', avatar: '', inviteCount: 15, rank: 4 },
  { id: 'user_005', nickname: '刘哥', avatar: '', inviteCount: 12, rank: 5 },
  { id: 'user_006', nickname: '陈婶', avatar: '', inviteCount: 10, rank: 6 },
  { id: 'user_007', nickname: '周大爷', avatar: '', inviteCount: 8, rank: 7 },
  { id: 'user_008', nickname: '吴姐', avatar: '', inviteCount: 6, rank: 8 }
];

/**
 * Mock API 类
 */
class MockApi {
  constructor() {
    this.initData();
  }

  initData() {
    if (!wx.getStorageSync(STORAGE_KEYS.GIFTS)) {
      wx.setStorageSync(STORAGE_KEYS.GIFTS, DEFAULT_GIFTS);
    }
    if (!wx.getStorageSync(STORAGE_KEYS.INVITES)) {
      wx.setStorageSync(STORAGE_KEYS.INVITES, []);
    }
    if (!wx.getStorageSync(STORAGE_KEYS.CLAIMED)) {
      wx.setStorageSync(STORAGE_KEYS.CLAIMED, []);
    }
  }

  getCurrentUser() {
    return wx.getStorageSync(STORAGE_KEYS.USER) || null;
  }

  setCurrentUser(user) {
    wx.setStorageSync(STORAGE_KEYS.USER, user);
  }

  // 手机号登录
  async phoneLogin(code) {
    await delay(500);
    const user = {
      id: 'mock_user_' + Date.now(),
      nickname: '新用户' + Math.floor(Math.random() * 1000),
      avatar: '',
      phone: '138****' + Math.floor(Math.random() * 10000).toString().padStart(4, '0'),
      inviteCode: this.generateInviteCode(),
      inviteCount: 0,
      createdAt: new Date().toISOString()
    };
    this.setCurrentUser(user);
    return { success: true, data: user };
  }

  generateInviteCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
  }

  async getUserInfo() {
    await delay(200);
    const user = this.getCurrentUser();
    if (!user) return { success: false, message: '未登录' };
    const invites = wx.getStorageSync(STORAGE_KEYS.INVITES) || [];
    user.inviteCount = invites.filter(i => i.inviterCode === user.inviteCode).length;
    return { success: true, data: user };
  }

  // 绑定邀请关系
  async bindInvite(inviterCode) {
    await delay(300);
    const user = this.getCurrentUser();
    if (!user) return { success: false, message: '请先登录' };
    if (user.invitedBy) return { success: false, message: '已绑定邀请人' };
    if (user.inviteCode === inviterCode) return { success: false, message: '不能邀请自己' };

    user.invitedBy = inviterCode;
    this.setCurrentUser(user);

    const invites = wx.getStorageSync(STORAGE_KEYS.INVITES) || [];
    invites.push({
      id: 'invite_' + Date.now(),
      inviterCode: inviterCode,
      inviteeId: user.id,
      inviteeName: user.nickname,
      createdAt: new Date().toISOString()
    });
    wx.setStorageSync(STORAGE_KEYS.INVITES, invites);
    return { success: true, message: '绑定成功' };
  }

  async getMyInvites() {
    await delay(300);
    const user = this.getCurrentUser();
    if (!user) return { success: false, message: '请先登录' };
    const invites = wx.getStorageSync(STORAGE_KEYS.INVITES) || [];
    const myInvites = invites.filter(i => i.inviterCode === user.inviteCode);
    return { success: true, data: { total: myInvites.length, list: myInvites } };
  }

  // 模拟新增邀请（测试用）
  async simulateNewInvite() {
    await delay(100);
    const user = this.getCurrentUser();
    if (!user) return { success: false, message: '请先登录' };

    const invites = wx.getStorageSync(STORAGE_KEYS.INVITES) || [];
    invites.push({
      id: 'invite_' + Date.now(),
      inviterCode: user.inviteCode,
      inviteeId: 'sim_user_' + Date.now(),
      inviteeName: '模拟用户' + Math.floor(Math.random() * 100),
      createdAt: new Date().toISOString()
    });
    wx.setStorageSync(STORAGE_KEYS.INVITES, invites);

    user.inviteCount = invites.filter(i => i.inviterCode === user.inviteCode).length;
    this.setCurrentUser(user);
    return { success: true };
  }

  async getGiftList() {
    await delay(300);
    const user = this.getCurrentUser();
    const gifts = wx.getStorageSync(STORAGE_KEYS.GIFTS) || DEFAULT_GIFTS;
    const claimed = wx.getStorageSync(STORAGE_KEYS.CLAIMED) || [];
    const invites = wx.getStorageSync(STORAGE_KEYS.INVITES) || [];
    const inviteCount = user ? invites.filter(i => i.inviterCode === user.inviteCode).length : 0;

    const giftList = gifts.map(gift => {
      const claimRecord = claimed.find(c => c.giftId === gift.id && c.userId === (user?.id || ''));
      let status = 'locked';
      if (claimRecord) status = 'claimed';
      else if (inviteCount >= gift.requiredInvites) status = 'unlocked';

      return {
        ...gift,
        status,
        progress: Math.min(100, Math.round((inviteCount / gift.requiredInvites) * 100)),
        progressText: `${inviteCount}/${gift.requiredInvites}人`,
        claimedAt: claimRecord?.claimedAt,
        code: claimRecord?.code
      };
    });
    return { success: true, data: giftList };
  }

  async getGiftDetail(giftId) {
    await delay(200);
    const result = await this.getGiftList();
    const gift = result.data.find(g => g.id === giftId);
    if (!gift) return { success: false, message: '礼品不存在' };
    gift.conditionText = `成功邀请 ${gift.requiredInvites} 位好友即可领取`;
    gift.expireAt = this.getExpireDate(7);
    return { success: true, data: gift };
  }

  async claimGift(giftId) {
    await delay(500);
    const user = this.getCurrentUser();
    if (!user) return { success: false, message: '请先登录' };

    const gifts = wx.getStorageSync(STORAGE_KEYS.GIFTS) || DEFAULT_GIFTS;
    const gift = gifts.find(g => g.id === giftId);
    if (!gift) return { success: false, message: '礼品不存在' };

    const invites = wx.getStorageSync(STORAGE_KEYS.INVITES) || [];
    const myInviteCount = invites.filter(i => i.inviterCode === user.inviteCode).length;
    if (myInviteCount < gift.requiredInvites) {
      return { success: false, message: `还需邀请 ${gift.requiredInvites - myInviteCount} 人` };
    }

    const claimed = wx.getStorageSync(STORAGE_KEYS.CLAIMED) || [];
    if (claimed.find(c => c.giftId === giftId && c.userId === user.id)) {
      return { success: false, message: '已领取过该礼品' };
    }

    const code = this.generateClaimCode();
    const claimRecord = {
      id: 'claim_' + Date.now(),
      giftId, giftName: gift.name, userId: user.id, code,
      claimedAt: this.formatDate(new Date()),
      expireAt: this.getExpireDate(7),
      status: 'unused'
    };
    claimed.push(claimRecord);
    wx.setStorageSync(STORAGE_KEYS.CLAIMED, claimed);
    return { success: true, data: claimRecord, message: '领取成功' };
  }

  generateClaimCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789';
    let code = 'JH';
    for (let i = 0; i < 8; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
  }

  async getMyGifts() {
    await delay(300);
    const user = this.getCurrentUser();
    if (!user) return { success: false, message: '请先登录' };
    const claimed = wx.getStorageSync(STORAGE_KEYS.CLAIMED) || [];
    return { success: true, data: claimed.filter(c => c.userId === user.id) };
  }

  async getRanking(type = 'week') {
    await delay(400);
    const user = this.getCurrentUser();
    let ranking = [...DEFAULT_RANKING];

    if (user) {
      const invites = wx.getStorageSync(STORAGE_KEYS.INVITES) || [];
      const myCount = invites.filter(i => i.inviterCode === user.inviteCode).length;
      if (myCount > 0) {
        ranking.push({
          id: user.id, nickname: user.nickname + '(我)',
          avatar: user.avatar, inviteCount: myCount, isMe: true
        });
      }
    }

    ranking.sort((a, b) => b.inviteCount - a.inviteCount);
    ranking = ranking.map((item, index) => ({ ...item, rank: index + 1 }));
    const myRank = ranking.find(r => r.isMe);

    return {
      success: true,
      data: {
        list: ranking.slice(0, 20),
        myRank: myRank ? myRank.rank : null,
        myInviteCount: user?.inviteCount || 0
      }
    };
  }

  formatDate(date) {
    const d = new Date(date);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  }

  getExpireDate(days) {
    const d = new Date();
    d.setDate(d.getDate() + days);
    return this.formatDate(d);
  }

  resetAllData() {
    wx.removeStorageSync(STORAGE_KEYS.USER);
    wx.removeStorageSync(STORAGE_KEYS.INVITES);
    wx.removeStorageSync(STORAGE_KEYS.CLAIMED);
    wx.removeStorageSync(STORAGE_KEYS.GIFTS);
    this.initData();
  }
}

const mockApi = new MockApi();
module.exports = mockApi;
