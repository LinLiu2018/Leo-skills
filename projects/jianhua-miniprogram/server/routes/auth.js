const express = require('express');
const router = express.Router();
const axios = require('axios');
const jwt = require('jsonwebtoken');
const db = require('../config/database');

// 生成邀请码
function generateInviteCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
}

// 手机号登录
router.post('/phone-login', async (req, res) => {
  try {
    const { code, inviteCode } = req.body;

    // 调用微信API获取手机号
    // 实际开发需要先获取access_token，再调用getPhoneNumber
    // 这里简化处理，假设已获取到手机号
    const phone = '138' + Math.random().toString().slice(2, 10);

    // 查找或创建用户
    let [users] = await db.execute('SELECT * FROM users WHERE phone = ?', [phone]);
    let user;
    let isNewUser = false;

    if (users.length === 0) {
      // 新用户
      isNewUser = true;
      const userInviteCode = generateInviteCode();

      const [result] = await db.execute(
        'INSERT INTO users (phone, invite_code, inviter_id) VALUES (?, ?, ?)',
        [phone, userInviteCode, null]
      );

      // 处理邀请关系
      if (inviteCode) {
        const [inviters] = await db.execute('SELECT id FROM users WHERE invite_code = ?', [inviteCode]);
        if (inviters.length > 0) {
          await db.execute('UPDATE users SET inviter_id = ? WHERE id = ?', [inviters[0].id, result.insertId]);
          // 增加邀请人的邀请数
          await db.execute('UPDATE users SET invite_count = invite_count + 1 WHERE id = ?', [inviters[0].id]);
        }
      }

      // 发放初始礼品
      const expireDate = new Date();
      expireDate.setDate(expireDate.getDate() + 7);

      await db.execute(
        'INSERT INTO user_gifts (user_id, gift_id, status, expire_at) VALUES (?, 1, "pending", ?)',
        [result.insertId, expireDate]
      );

      [users] = await db.execute('SELECT * FROM users WHERE id = ?', [result.insertId]);
    }

    user = users[0];

    // 生成token
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '30d' });

    // 获取用户礼品
    const [gifts] = await db.execute(
      `SELECT ug.*, g.name, g.description FROM user_gifts ug
       JOIN gifts g ON ug.gift_id = g.id
       WHERE ug.user_id = ? AND ug.status = 'pending' LIMIT 1`,
      [user.id]
    );

    res.json({
      success: true,
      user: {
        id: user.id,
        phone: user.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2'),
        nickname: user.nickname || '微信用户',
        invite_code: user.invite_code,
        is_new_user: isNewUser,
        initial_gift: gifts.length > 0 ? {
          name: gifts[0].name,
          code: `GIFT${gifts[0].id.toString().padStart(6, '0')}`,
          expire_at: gifts[0].expire_at
        } : null
      },
      token,
      message: isNewUser ? '恭喜获得抽纸1包，快分享给好友解锁更多礼品吧！' : '登录成功'
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

module.exports = router;
