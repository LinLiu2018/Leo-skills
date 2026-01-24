
import React, { useState, useEffect } from 'react';

// 定义用户角色类型
type UserRole = 'admin' | 'analyst' | 'visitor' | 'custom';

// 定义断点类型
type BreakpointType = 'panorama' | 'workspace' | 'focus' | 'minimal';

interface DashboardLayoutProps {
  userRole?: UserRole;
  children: React.ReactNode;
  initialBreakpoint?: BreakpointType;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  userRole = 'analyst',
  children,
  initialBreakpoint
}) => {
  // 状态管理
  const [currentBreakpoint, setCurrentBreakpoint] = useState<BreakpointType>('workspace');
  const [isCollaborating, setIsCollaborating] = useState(false);
  const [aiConfidence, setAiConfidence] = useState(0.85);
  const [syncStatus, setSyncStatus] = useState<'full' | 'partial' | 'offline' | 'conflict'>('full');
  
  // 断点配置映射
  const breakpointConfig = {
    panorama: { cols: 16, margin: '32px', maxWidth: '100%' },
    workspace: { cols: 12, margin: '24px', maxWidth: '1439px' },
    focus: { cols: 8, margin: '16px', maxWidth: '1023px' },
    minimal: { cols: 4, margin: '12px', maxWidth: '767px' }
  };

  // 监听窗口大小变化
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      let newBreakpoint: BreakpointType = 'workspace';
      
      if (width >= 1440) newBreakpoint = 'panorama';
      else if (width >= 1024) newBreakpoint = 'workspace';
      else if (width >= 768) newBreakpoint = 'focus';
      else newBreakpoint = 'minimal';
      
      setCurrentBreakpoint(newBreakpoint);
    };

    // 初始化断点
    if (initialBreakpoint) {
      setCurrentBreakpoint(initialBreakpoint);
    } else {
      handleResize();
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [initialBreakpoint]);

  // 获取当前配置
  const config = breakpointConfig[currentBreakpoint];

  // 同步状态样式
  const syncStatusStyles = {
    full: 'bg-green-500 animate-pulse ring-2 ring-green-300',
    partial: 'bg-yellow-500 animate-pulse',
    offline: 'bg-blue-500',
    conflict: 'bg-red-500 animate-pulse ring-2 ring-red-300'
  };

  // 置信度颜色计算
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  // 网格列生成
  const gridColsClass = `grid grid-cols-${config.cols} gap-4`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* 顶部导航栏 */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className={`mx-auto px-${config.margin.split('px')[0]}`}>
          <div className="flex items-center justify-between h-16">
            {/* 左侧：品牌和用户信息 */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 
                  ${currentBreakpoint === 'minimal' ? 'mr-2' : 'mr-4'}`} />
                {currentBreakpoint !== 'minimal' && (
                  <span className="text-xl font-semibold text-gray-800">AI智能体仪表板</span>
                )}
              </div>
              
              {/* 用户角色标识 */}
              <div className={`px-3 py-1 rounded-full text-sm font-medium
                ${userRole === 'admin' ? 'bg-purple-100 text-purple-800' : 
                  userRole === 'analyst' ? 'bg-blue-100 text-blue-800' : 
                  'bg-gray-100 text-gray-800'}`}>
                {userRole === 'admin' ? '管理员' : 
                 userRole === 'analyst' ? '分析师' : '访客'}
              </div>
            </div>

            {/* 中间：状态指示器 */}
            <div className="flex items-center space-x-6">
              {/* AI置信度指示器 */}
              <div className="flex items-center space-x-2">
                <div className="text-sm text-gray-600">AI置信度</div>
                <div className={`text-lg font-bold ${getConfidenceColor(aiConfidence)}`}>
                  {(aiConfidence * 100).toFixed(1)}%
                </div>
                <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      aiConfidence >= 0.8 ? 'bg-green-500' : 
                      aiConfidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${aiConfidence * 100}%` }}
                  />
                </div>
              </div>

              {/* 同步状态 */}
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${syncStatusStyles[syncStatus]}`} />
                <span className="text-sm text-gray-600">
                  {syncStatus === 'full' ? '全同步' :
                   syncStatus === 'partial' ? '部分同步' :
                   syncStatus === 'offline' ? '离线编辑' : '冲突待解'}
                </span>
              </div>
            </div>

            {/* 右侧：操作按钮 */}
            <div className="flex items-center space-x-3">
              {/* 协作模式切换 */}
              <button
                onClick={() => setIsCollaborating(!isCollaborating)}
                className={`px-4 py-2 rounded-lg transition-all ${
                  isCollaborating 
                    ? 'bg-green-100 text-green-800 border border-green-300' 
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`}
              >
                {isCollaborating ? '协作中...' : '开启协作'}
              </button>

              {/* 伦理透明度入口 */}
              <button className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors">
                <div className="w-5 h-5 rounded-full bg-gradient-to-r from-blue-400 to-cyan-400" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区域 */}
      <main className={`mx-auto py-6 px-${config.margin.split('px')[0]}`}>
        {/* 自适应网格容器 */}
        <div className={gridColsClass}>
          {children}
        </div>

        {/* 边缘计算状态栏（底部） */}
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2">
          <div className="flex items-center space-x-4 px-4 py-2 bg-white/90 backdrop-blur-sm 
            rounded-full shadow-lg border border-gray-200">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-gray-600">边缘计算在线</span>
            </div>
            <div className="text-sm text-gray-500">|</div>
            <div className="text-sm text-gray-600">
              当前模式：{currentBreakpoint === 'panorama' ? '全景模式' :
                       currentBreakpoint === 'workspace' ? '工作台模式' :
                       currentBreakpoint === 'focus' ? '聚焦模式' : '极简模式'}
            </div>
          </div>
        </div>

        {/* 多模态交互提示 */}
        {currentBreakpoint !== 'minimal' && (
          <div className="fixed bottom-4 right-4">
            <div className="text-xs text-gray-500 bg-white/80 backdrop-blur-sm 
              px-3 py-2 rounded-lg border border-gray-200">
              提示：尝试语音唤醒词"分析助手"或五指收拢手势
            </div>
          </div>
        )}
      </main>

      {/* 无障碍访问提示 */}
      <div className="sr-only" aria-live="polite">
        当前仪表板布局已适配{currentBreakpoint}模式，使用{config.cols}列网格系统
      </div>
    </div>
  );
};

// 示例使用组件
export const DashboardModule: React.FC<{
  colSpan?: number;
  rowSpan?: number;
  title: string;
  children: React.ReactNode;
}> = ({ colSpan = 4, rowSpan = 1, title, children }) => {
  return (
    <div 
      className={`col-span-${colSpan} row-span-${rowSpan} bg-white rounded-xl shadow-sm 
        border border-gray-200 p-4 hover:shadow-md transition-shadow`}
    >
      <h3 className="text-lg font-semibold text-gray-800 mb-3">{title}</h3>
      <div className="text-gray-600 h-full">{children}</div>
    </div>
  );
};

export default DashboardLayout;