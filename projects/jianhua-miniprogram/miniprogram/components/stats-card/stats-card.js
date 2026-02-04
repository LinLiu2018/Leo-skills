// components/stats-card/stats-card.js
Component({
  properties: {
    // 标题
    title: {
      type: String,
      value: ''
    },
    // 图标（emoji）
    icon: {
      type: String,
      value: ''
    },
    // 主数值
    value: {
      type: String,
      value: '0'
    },
    // 单位
    unit: {
      type: String,
      value: ''
    },
    // 副文本
    subText: {
      type: String,
      value: ''
    },
    // 主题: default, primary
    theme: {
      type: String,
      value: 'default'
    },
    // 是否显示进度条
    showProgress: {
      type: Boolean,
      value: false
    },
    // 进度百分比
    progress: {
      type: Number,
      value: 0
    },
    // 进度文字
    progressText: {
      type: String,
      value: ''
    },
    // 多项统计数据 [{value, label}]
    items: {
      type: Array,
      value: []
    }
  }
})
