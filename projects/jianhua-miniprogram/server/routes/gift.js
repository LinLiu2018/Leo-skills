const express = require('express');
const router = express.Router();
const db = require('../config/database');
const auth = require('../middleware/auth');

// 礼品解锁规则
const GIFT_RULES = [
  { giftId: 1, required: 0, name: '抽纸1包' },
  { giftId: 2, required: 3, name: '洗衣液1瓶' },
  { giftId: 3, required: 10, name: '大米5斤' },
  { giftId: 4, required: 20, name: '食用油1桶' },
  { giftId: 5, required: 50, name: '神秘大奖' }
];

// 获取礼品进度
router.get('/progress', auth, async (req, res) => {
  try {
    const [users] = await db.execute('SELECT invite_count FROM users WHERE id = ?', [req.userId]);
    const inviteCount = users[0]?.invite_count || 0;

    // 获取已领取的礼品
    const [claimed] = await db.execute(
      'SELECT gift_id FROM user_gifts WHERE user_id = ?',
      [req.userId]
    );
    const claimedIds = claimed.map(c => c.gift_id);

    const gifts = GIFT_RULES.map(rule => ({
      id: rule.giftId,
      name: rule.name,
      required: rule.required,
      unlocked: inviteCount >= rule.required,
      claimed: claimedIds.includes(rule.giftId)
    }));

    // 计算下一个目标
    const nextGift = GIFT_RULES.find(r => inviteCount < r.required);

    res.json({
      success: true,
      inviteCount,
      gifts,
      nextTarget: nextGift ? nextGift.required : null,
      progress: nextGift ? Math.round((inviteCount / nextGift.required) * 100) : 100
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

// 领取礼品
router.post('/claim', auth, async (req, res) => {
  try {
    const { giftId } = req.body;

    const [users] = await db.execute('SELECT invite_count FROM users WHERE id = ?', [req.userId]);
    const inviteCount = users[0]?.invite_count || 0;

    const rule = GIFT_RULES.find(r => r.giftId === giftId);
    if (!rule) {
      return res.status(400).json({ success: false, message: '礼品不存在' });
    }

    if (inviteCount < rule.required) {
      return res.status(400).json({ success: false, message: '邀请人数不足' });
    }

    // 检查是否已领取
    const [existing] = await db.execute(
      'SELECT id FROM user_gifts WHERE user_id = ? AND gift_id = ?',
      [req.userId, giftId]
    );

    if (existing.length > 0) {
      return res.status(400).json({ success: false, message: '已领取过该礼品' });
    }

    // 发放礼品
    const expireDate = new Date();
    expireDate.setDate(expireDate.getDate() + 7);

    await db.execute(
      'INSERT INTO user_gifts (user_id, gift_id, status, expire_at) VALUES (?, ?, "pending", ?)',
      [req.userId, giftId, expireDate]
    );

    res.json({
      success: true,
      message: `恭喜获得${rule.name}，请预约到访领取！`
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

// 获取用户礼品列表
router.get('/list', auth, async (req, res) => {
  try {
    const [gifts] = await db.execute(
      `SELECT ug.*, g.name, g.description FROM user_gifts ug
       JOIN gifts g ON ug.gift_id = g.id
       WHERE ug.user_id = ? ORDER BY ug.created_at DESC`,
      [req.userId]
    );

    res.json({
      success: true,
      gifts: gifts.map(g => ({
        id: g.id,
        name: g.name,
        status: g.status,
        statusText: g.status === 'pending' ? '待领取' : '已领取',
        expire: g.expire_at
      }))
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

// 获取领取动态
router.get('/dynamics', async (req, res) => {
  try {
    const [dynamics] = await db.execute(
      `SELECT u.phone, g.name, ug.created_at FROM user_gifts ug
       JOIN users u ON ug.user_id = u.id
       JOIN gifts g ON ug.gift_id = g.id
       ORDER BY ug.created_at DESC LIMIT 10`
    );

    const [total] = await db.execute('SELECT COUNT(*) as count FROM user_gifts');

    res.json({
      success: true,
      total: total[0].count,
      dynamics: dynamics.map(d => ({
        name: d.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2').slice(0, 3) + '*' + d.phone.slice(-1),
        gift: d.name,
        time: formatTime(d.created_at)
      }))
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

function formatTime(date) {
  const now = new Date();
  const diff = (now - new Date(date)) / 1000;
  if (diff < 60) return '刚刚';
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前';
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前';
  return Math.floor(diff / 86400) + '天前';
}

module.exports = router;
