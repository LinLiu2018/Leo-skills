const express = require('express');
const router = express.Router();
const db = require('../config/database');
const auth = require('../middleware/auth');

// 获取用户信息
router.get('/info', auth, async (req, res) => {
  try {
    const [users] = await db.execute('SELECT * FROM users WHERE id = ?', [req.userId]);
    if (users.length === 0) {
      return res.status(404).json({ success: false, message: '用户不存在' });
    }

    const user = users[0];

    // 获取统计数据
    const [giftCount] = await db.execute(
      'SELECT COUNT(*) as count FROM user_gifts WHERE user_id = ?',
      [req.userId]
    );

    const [visitCount] = await db.execute(
      'SELECT COUNT(*) as count FROM appointments WHERE user_id = ? AND status = "completed"',
      [req.userId]
    );

    res.json({
      success: true,
      user: {
        id: user.id,
        phone: user.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2'),
        nickname: user.nickname || '微信用户',
        invite_code: user.invite_code,
        invite_count: user.invite_count
      },
      stats: {
        inviteCount: user.invite_count,
        giftCount: giftCount[0].count,
        visitCount: visitCount[0].count
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

// 获取邀请列表
router.get('/invites', auth, async (req, res) => {
  try {
    const [invites] = await db.execute(
      `SELECT id, phone, created_at FROM users WHERE inviter_id = ? ORDER BY created_at DESC LIMIT 50`,
      [req.userId]
    );

    res.json({
      success: true,
      invites: invites.map(i => ({
        id: i.id,
        phone: i.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2'),
        time: i.created_at
      }))
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

module.exports = router;
