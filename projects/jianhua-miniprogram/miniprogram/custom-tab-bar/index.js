Component({
  data: {
    selected: 0,
    color: "#999999",
    selectedColor: "#FF6B35",
    list: [{
      pagePath: "/pages/index/index",
      iconPath: "https://placehold.co/60x60/999999/ffffff?text=Home",
      selectedIconPath: "https://placehold.co/60x60/FF6B35/ffffff?text=Home",
      text: "首页"
    }, {
      pagePath: "/pages/share/share",
      iconPath: "https://placehold.co/60x60/999999/ffffff?text=Gift",
      selectedIconPath: "https://placehold.co/60x60/FF6B35/ffffff?text=Gift",
      text: "分享"
    }, {
      pagePath: "/pages/user/user",
      iconPath: "https://placehold.co/60x60/999999/ffffff?text=Me",
      selectedIconPath: "https://placehold.co/60x60/FF6B35/ffffff?text=Me",
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
