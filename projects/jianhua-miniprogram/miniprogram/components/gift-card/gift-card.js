// components/gift-card/gift-card.js
Component({
  properties: {
    // 礼品名称
    name: {
      type: String,
      value: ''
    },
    // 礼品图片
    image: {
      type: String,
      value: ''
    },
    // 礼品描述
    desc: {
      type: String,
      value: ''
    },
    // 领取条件文字
    condition: {
      type: String,
      value: ''
    },
    // 角标文字
    badge: {
      type: String,
      value: ''
    },
    // 尺寸: small, medium, large
    size: {
      type: String,
      value: 'medium'
    },
    // 状态: locked, unlocked, claimed
    status: {
      type: String,
      value: ''
    },
    // 是否显示进度条
    showProgress: {
      type: Boolean,
      value: false
    },
    // 进度百分比 0-100
    progress: {
      type: Number,
      value: 0
    },
    // 进度文字
    progressText: {
      type: String,
      value: ''
    },
    // 操作按钮文字
    actionText: {
      type: String,
      value: ''
    },
    // 按钮类型: primary, secondary, disabled
    actionType: {
      type: String,
      value: 'primary'
    },
    // 按钮是否禁用
    actionDisabled: {
      type: Boolean,
      value: false
    },
    // 礼品数据（用于事件传递）
    giftData: {
      type: Object,
      value: {}
    }
  },

  methods: {
    onAction() {
      this.triggerEvent('action', this.data.giftData)
    }
  }
})
