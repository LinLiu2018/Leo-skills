Component({
  data: {
    selected: 0,
    color: "#999999",
    selectedColor: "#FF6B35",
    list: [{
      pagePath: "/pages/index/index",
      icon: "🏠",
      text: "首页"
    }, {
      pagePath: "/pages/share/share",
      icon: "🎁",
      text: "分享"
    }, {
      pagePath: "/pages/user/user",
      icon: "👤",
      text: "我的"
    }]
  },
  methods: {
    switchTab(e) {
      const data = e.currentTarget.dataset
      const url = data.path
      wx.switchTab({url})
      this.setData({
        selected: data.index
      })
    }
  }
})
