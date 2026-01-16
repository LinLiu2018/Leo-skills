const express = require('express');
const router = express.Router();
const db = require('../config/database');
const auth = require('../middleware/auth');

// 生成预约码
function generateAppointmentCode() {
  return 'YY' + Date.now().toString().slice(-8);
}

// 创建预约
router.post('/create', auth, async (req, res) => {
  try {
    const { date, timeSlot, name, giftId } = req.body;

    if (!date || !timeSlot || !name) {
      return res.status(400).json({ success: false, message: '请填写完整信息' });
    }

    // 检查是否有待完成的预约
    const [existing] = await db.execute(
      'SELECT id FROM appointments WHERE user_id = ? AND status = "pending"',
      [req.userId]
    );

    if (existing.length > 0) {
      return res.status(400).json({ success: false, message: '您已有待完成的预约' });
    }

    const code = generateAppointmentCode();

    await db.execute(
      `INSERT INTO appointments (user_id, appointment_date, time_slot, contact_name, code, gift_id, status)
       VALUES (?, ?, ?, ?, ?, ?, 'pending')`,
      [req.userId, date, timeSlot, name, code, giftId || null]
    );

    res.json({
      success: true,
      appointment: { date, timeSlot, name, code },
      message: '预约成功，请按时到访'
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

// 获取预约信息
router.get('/info', auth, async (req, res) => {
  try {
    const [appointments] = await db.execute(
      `SELECT a.*, g.name as gift_name FROM appointments a
       LEFT JOIN gifts g ON a.gift_id = g.id
       WHERE a.user_id = ? AND a.status = 'pending'
       ORDER BY a.created_at DESC LIMIT 1`,
      [req.userId]
    );

    if (appointments.length === 0) {
      return res.json({ success: true, hasAppointment: false });
    }

    const apt = appointments[0];
    res.json({
      success: true,
      hasAppointment: true,
      appointment: {
        id: apt.id,
        date: apt.appointment_date,
        time: apt.time_slot,
        name: apt.contact_name,
        code: apt.code,
        gift: apt.gift_name || '抽纸1包',
        status: apt.status
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

// 取消预约
router.post('/cancel', auth, async (req, res) => {
  try {
    const { appointmentId } = req.body;

    await db.execute(
      'UPDATE appointments SET status = "cancelled" WHERE id = ? AND user_id = ?',
      [appointmentId, req.userId]
    );

    res.json({ success: true, message: '预约已取消' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

module.exports = router;
