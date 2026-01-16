// pages/appointment/appointment.js
const app = getApp();

Page({
  data: {
    hasAppointment: false,
    giftName: '',
    expireDate: '',
    phone: '',
    name: '',
    dateList: [],
    timeSlots: ['09:00-10:00', '10:00-11:00', '11:00-12:00', '14:00-15:00', '15:00-16:00', '16:00-17:00'],
    selectedDate: '',
    selectedTime: '',
    appointmentInfo: null
  },

  onLoad(options) {
    this.initData();
    this.generateDateList();

    if (options.gift) {
      this.setData({ giftName: decodeURIComponent(options.gift) });
    }
  },

  initData() {
    const userInfo = app.globalData.userInfo || {};
    const gift = userInfo.initial_gift || {};

    this.setData({
      phone: userInfo.phone || '未登录',
      giftName: gift.name || '抽纸1包',
      expireDate: gift.expire_at || '2026-01-22'
    });

    // 检查是否已有预约
    const appointment = wx.getStorageSync('appointment');
    if (appointment) {
      this.setData({
        hasAppointment: true,
        appointmentInfo: appointment
      });
    }
  },

  generateDateList() {
    const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    const dateList = [];
    const today = new Date();

    for (let i = 1; i <= 7; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);

      const month = date.getMonth() + 1;
      const day = date.getDate();
      const dateStr = `${month}月${day}日`;

      dateList.push({
        date: `${date.getFullYear()}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
        week: i === 1 ? '明天' : weekDays[date.getDay()],
        day: dateStr
      });
    }

    this.setData({
      dateList,
      selectedDate: dateList[0].date
    });
  },

  selectDate(e) {
    this.setData({ selectedDate: e.currentTarget.dataset.date });
  },

  selectTime(e) {
    const time = e.currentTarget.dataset.time;
    if (!time.disabled) {
      this.setData({ selectedTime: time });
    }
  },

  inputName(e) {
    this.setData({ name: e.detail.value });
  },

  submitAppointment() {
    const { selectedDate, selectedTime, name, phone, giftName } = this.data;

    if (!selectedDate) {
      wx.showToast({ title: '请选择日期', icon: 'none' });
      return;
    }
    if (!selectedTime) {
      wx.showToast({ title: '请选择时间段', icon: 'none' });
      return;
    }
    if (!name.trim()) {
      wx.showToast({ title: '请输入姓名', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '提交中...' });

    // Mock提交预约
    setTimeout(() => {
      const appointmentCode = 'YY' + Date.now().toString().slice(-8);
      const dateObj = this.data.dateList.find(d => d.date === selectedDate);

      const appointmentInfo = {
        date: dateObj ? dateObj.day : selectedDate,
        time: selectedTime,
        gift: giftName,
        code: appointmentCode,
        name: name,
        phone: phone
      };

      wx.setStorageSync('appointment', appointmentInfo);

      this.setData({
        hasAppointment: true,
        appointmentInfo: appointmentInfo
      });

      wx.hideLoading();
      wx.showToast({ title: '预约成功', icon: 'success' });
    }, 500);
  },

  openLocation() {
    wx.openLocation({
      latitude: 33.5513,
      longitude: 119.0153,
      name: '建华观园菜场售楼处',
      address: '淮安市清江浦区建华观园菜场'
    });
  },

  cancelAppointment() {
    wx.showModal({
      title: '取消预约',
      content: '确定要取消预约吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('appointment');
          this.setData({
            hasAppointment: false,
            appointmentInfo: null,
            selectedTime: ''
          });
          wx.showToast({ title: '已取消', icon: 'success' });
        }
      }
    });
  }
});
