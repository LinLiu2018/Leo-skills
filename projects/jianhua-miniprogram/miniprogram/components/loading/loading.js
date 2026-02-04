// components/loading/loading.js
Component({
  properties: {
    // 类型: loading, empty, error, skeleton
    type: {
      type: String,
      value: 'loading'
    },
    // 提示文字
    text: {
      type: String,
      value: ''
    },
    // 图标（emoji）
    icon: {
      type: String,
      value: ''
    },
    // 操作按钮文字
    actionText: {
      type: String,
      value: ''
    },
    // 骨架屏是否显示头像
    showAvatar: {
      type: Boolean,
      value: true
    }
  },

  methods: {
    onAction() {
      this.triggerEvent('action')
    },
    onRetry() {
      this.triggerEvent('retry')
    }
  }
})
