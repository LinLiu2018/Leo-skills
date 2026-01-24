// form.js
const app = getApp()

Page({
  data: {
    pageTitle: '信息填写',
    formData: { 'name': '', 'phone': '', 'demand': '' },
    loading: false,
    options: {}
  },

  onLoad(options) {
    // 获取URL参数（如推荐人ID）
    if (options.pid) {
      this.setData({ 'formData.parent_id': options.pid })
    }
  },

  // 输入框变化
  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({
      [`formData.${field}`]: e.detail.value
    })
  },

  // 表单提交
  async onSubmit(e) {
    const { formData } = this.data

    // 验证
    if (!this.validateForm(formData)) {
      return
    }

    this.setData({ loading: true })

    try {
      const res = await wx.request({
        url: app.globalData.baseUrl + '/api/leads',
        method: 'POST',
        data: formData
      })

      if (res.data.success) {
        wx.showToast({ title: '提交成功', icon: 'success' })
        // 跳转到结果页
        wx.navigateTo({
          url: `/pages/result/result?id=${res.data.data.id}`
        })
      } else {
        wx.showToast({ title: res.data.error || '提交失败', icon: 'none' })
      }
    } catch (err) {
      wx.showToast({ title: '网络错误', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 表单验证
  validateForm(data) {
    if (!data.name) {
      wx.showToast({ title: '请输入姓名', icon: 'none' })
      return false
    }
    if (!data.phone || !/^1[3-9]\d{9}$/.test(data.phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return false
    }
    return true
  }
})
