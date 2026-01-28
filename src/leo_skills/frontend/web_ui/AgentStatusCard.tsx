```tsx
import React from 'react';

interface AgentStatusCardProps {
  agentName: string;
  status: 'online' | 'offline' | 'busy' | 'error';
  confidence?: number; // 置信度 0-1
  lastSync?: string; // 最后同步时间
  isEdgeDevice?: boolean; // 是否为边缘设备
  onDetailsClick?: () => void;
  onControlClick?: () => void;
}

const AgentStatusCard: React.FC<AgentStatusCardProps> = ({
  agentName,
  status,
  confidence = 0.95,
  lastSync = '刚刚',
  isEdgeDevice = false,
  onDetailsClick,
  onControlClick
}) => {
  // 状态配置映射
  const statusConfig = {
    online: {
      label: '在线',
      color: 'bg-green-500',
      pulse: true,
      icon: '🟢'
    },
    offline: {
      label: '离线',
      color: 'bg-gray-400',
      pulse: false,
      icon: '⚫'
    },
    busy: {
      label: '忙碌',
      color: 'bg-yellow-500',
      pulse: true,
      icon: '🟡'
    },
    error: {
      label: '错误',
      color: 'bg-red-500',
      pulse: false,
      icon: '🔴'
    }
  };

  const currentStatus = statusConfig[status];
  
  // 根据置信度计算透明度（遵循设计令牌规范）
  const getConfidenceStyle = () => {
    if (confidence >= 0.8) return 'bg-blue-600/90'; // high
    if (confidence >= 0.5) return 'bg-blue-600/60'; // medium
    return 'bg-blue-600/30'; // low
  };

  // 同步状态标识（遵循边缘计算适配方案）
  const getSyncIndicator = () => {
    if (status === 'offline') {
      return (
        <div className="flex items-center">
          <div className="w-2 h-2 bg-blue-500 rounded-full mr-1"></div>
          <span className="text-xs text-blue-500">离线编辑</span>
        </div>
      );
    }
    return (
      <div className="flex items-center">
        <div className={`w-2 h-2 rounded-full mr-1 ${currentStatus.pulse ? 'animate-pulse' : ''} ${currentStatus.color}`}></div>
        <span className="text-xs text-gray-600">同步于 {lastSync}</span>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-100 hover:shadow-xl transition-all duration-300">
      {/* 卡片头部 */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-gray-800">{agentName}</h3>
            {isEdgeDevice && (
              <span className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded-full">
                边缘设备
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-sm text-gray-500">{currentStatus.icon} {currentStatus.label}</span>
            {getSyncIndicator()}
          </div>
        </div>
        
        {/* 置信度指示器 */}
        <div className="flex flex-col items-end">
          <div className="text-xs text-gray-500 mb-1">置信度</div>
          <div className="relative w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full ${getConfidenceStyle()} transition-all duration-500`}
              style={{ width: `${confidence * 100}%` }}
            ></div>
          </div>
          <div className="text-xs font-medium mt-1">{Math.round(confidence * 100)}%</div>
        </div>
      </div>

      {/* 状态详情 */}
      <div className="mb-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-xs text-gray-500 mb-1">任务队列</div>
            <div className="text-sm font-medium">12 个</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-xs text-gray-500 mb-1">响应时间</div>
            <div className="text-sm font-medium">128ms</div>
          </div>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-2">
        <button
          onClick={onDetailsClick}
          className="flex-1 py-2 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center justify-center gap-1"
          aria-label={`查看${agentName}的详细信息`}
        >
          <span>📊</span>
          详情分析
        </button>
        <button
          onClick={onControlClick}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center justify-center gap-1 ${
            status === 'offline' || status === 'error'
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-blue-50 hover:bg-blue-100 text-blue-600'
          }`}
          aria-label={`控制${agentName}`}
          disabled={status === 'offline' || status === 'error'}
        >
          <span>🎮</span>
          控制面板
        </button>
      </div>

      {/* 伦理透明度提示（遵循伦理透明化设计原则） */}
      {confidence < 0.7 && (
        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-100 rounded-lg flex items-start gap-2">
          <span className="text-yellow-500">⚠️</span>
          <div className="text-xs text-yellow-700">
            <div className="font-medium">置信度偏低</div>
            <div>建议人工复核决策节点</div>
          </div>
        </div>
      )}

      {/* 无障碍支持：键盘导航提示 */}
      <div className="sr-only" aria-live="polite">
        {agentName}智能体状态：{currentStatus.label}，置信度{Math.round(confidence * 100)}%，最后同步时间{lastSync}
      </div>
    </div>
  );
};

export default AgentStatusCard;
```

## 组件特性说明

### 1. **遵循设计规范**
- **智能情境感知**：根据置信度动态调整透明度（`--ai-transparency-*`）
- **伦理透明化**：置信度低于阈值时显示预警提示
- **边缘计算适配**：离线状态显示蓝色静态标识

### 2. **技术特性**
- **TypeScript类型安全**：完整的Props接口定义
- **Tailwind CSS**：使用实用类实现响应式设计
- **无障碍支持**：
  - `sr-only` 屏幕阅读器内容
  - `aria-label` 和 `aria-live` 属性
  - 键盘导航支持

### 3. **交互设计**
- **状态可视化**：脉冲动画、颜色编码、图标标识
- **多通道反馈**：视觉状态+文本描述+语义化颜色
- **认知负荷管理**：简化信息布局，重要数据突出显示

### 4. **扩展建议**
```tsx
// 使用示例
<AgentStatusCard
  agentName="数据分析助手"
  status="online"
  confidence={0.87}
  lastSync="2分钟前"
  isEdgeDevice={true}
  onDetailsClick={() => console.log('查看详情')}
  onControlClick={() => console.log('打开控制面板')}
/>
```

该组件完全遵循提供的设计系统规范，特别是智能情境感知、伦理透明化和边缘计算适配等核心原则，同时保持了React/Next.js的最佳实践和Tailwind CSS的现代化样式方案。