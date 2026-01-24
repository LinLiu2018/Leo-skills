import React, { useState, useEffect } from 'react';

interface TrendChartProps {
  /** 图表数据 */
  data: Array<{
    timestamp: string | Date;
    value: number;
    confidence?: number; // 置信度 0-1
    biasWarning?: boolean; // 偏见预警
  }>;
  /** 图表标题 */
  title?: string;
  /** 是否显示简化视图 */
  showSimplified?: boolean;
  /** 是否启用语音描述 */
  enableVoiceDescription?: boolean;
  /** 置信度阈值 */
  confidenceThreshold?: number;
  /** 自定义类名 */
  className?: string;
}

/**
 * 智能趋势图表组件
 * 遵循AI智能体仪表板设计系统规范
 */
const TrendChart: React.FC<TrendChartProps> = ({
  data,
  title = '趋势分析',
  showSimplified = false,
  enableVoiceDescription = true,
  confidenceThreshold = 0.7,
  className = '',
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [selectedPoint, setSelectedPoint] = useState<number | null>(null);
  const [simplifiedView, setSimplifiedView] = useState(showSimplified);

  // 无障碍语音描述
  useEffect(() => {
    if (enableVoiceDescription && selectedPoint !== null) {
      const point = data[selectedPoint];
      const confidenceText = point.confidence 
        ? `置信度${Math.round(point.confidence * 100)}%`
        : '';
      const biasText = point.biasWarning ? '存在偏见预警' : '';
      
      // 在实际项目中应使用Web Speech API
      console.log(`语音描述：${point.timestamp} 数值${point.value} ${confidenceText} ${biasText}`);
    }
  }, [selectedPoint, data, enableVoiceDescription]);

  // 计算图表参数
  const values = data.map(d => d.value);
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const valueRange = maxValue - minValue;
  
  // 时间格式化
  const formatTime = (timestamp: string | Date) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // 获取置信度颜色
  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'rgba(0, 120, 215, 0.6)'; // 默认中等透明度
    
    if (confidence < 0.5) return 'rgba(255, 107, 107, 0.3)'; // 低置信度
    if (confidence < confidenceThreshold) return 'rgba(255, 193, 7, 0.6)'; // 中等置信度
    return 'rgba(76, 175, 80, 0.9)'; // 高置信度
  };

  // 简化视图数据
  const displayData = simplifiedView 
    ? data.filter((_, index) => index % 3 === 0) // 每3个点取1个
    : data;

  return (
    <div 
      className={`bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 transition-all duration-300 ${className}`}
      role="region"
      aria-label={`趋势图表：${title}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 标题和工具栏 */}
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center space-x-3">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
            {title}
          </h2>
          
          {/* 置信度指示器 */}
          {data.some(d => d.confidence) && (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full animate-pulse" 
                   style={{
                     background: `conic-gradient(
                       #ff6b6b 0% 33%,
                       #ffc107 33% 66%,
                       #4caf50 66% 100%
                     )`
                   }} />
              <span className="text-sm text-gray-600 dark:text-gray-300">
                置信度指示
              </span>
            </div>
          )}
        </div>
        
        {/* 工具栏 */}
        <div className="flex space-x-2">
          {/* 简化视图切换 */}
          <button
            onClick={() => setSimplifiedView(!simplifiedView)}
            className="px-3 py-1 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            aria-label={simplifiedView ? '切换到详细视图' : '切换到简化视图'}
          >
            {simplifiedView ? '详细视图' : '简化视图'}
          </button>
          
          {/* 偏见预警指示器 */}
          {data.some(d => d.biasWarning) && (
            <div className="px-3 py-1 text-sm rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 flex items-center">
              <span className="w-2 h-2 rounded-full bg-red-500 mr-2 animate-pulse" />
              偏见预警
            </div>
          )}
        </div>
      </div>
      
      {/* 图表容器 */}
      <div className="relative h-64 w-full" role="img" aria-label="趋势数据可视化">
        {/* 网格线 */}
        <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
            <div 
              key={ratio}
              className="border-t border-gray-200 dark:border-gray-700 w-full"
              style={{ top: `${ratio * 100}%` }}
            />
          ))}
        </div>
        
        {/* 数据线 */}
        <svg 
          className="absolute inset-0 w-full h-full transform"
          viewBox={`0 0 ${displayData.length * 50} 100`}
          preserveAspectRatio="none"
        >
          {/* 置信度背景区域 */}
          {displayData.map((point, index) => {
            if (!point.confidence || index === 0) return null;
            
            const prevPoint = displayData[index - 1];
            const x1 = (index - 1) * 50;
            const x2 = index * 50;
            const y1 = 100 - ((prevPoint.value - minValue) / valueRange * 100);
            const y2 = 100 - ((point.value - minValue) / valueRange * 100);
            
            return (
              <polygon
                key={`confidence-${index}`}
                points={`${x1},${y1} ${x2},${y2} ${x2},100 ${x1},100`}
                fill={getConfidenceColor(point.confidence)}
                fillOpacity="0.1"
              />
            );
          })}
          
          {/* 趋势线 */}
          <polyline
            points={displayData.map((point, index) => 
              `${index * 50},${100 - ((point.value - minValue) / valueRange * 100)}`
            ).join(' ')}
            fill="none"
            stroke="rgba(0, 120, 215, 0.8)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          
          {/* 数据点 */}
          {displayData.map((point, index) => {
            const x = index * 50;
            const y = 100 - ((point.value - minValue) / valueRange * 100);
            const hasBiasWarning = point.biasWarning;
            
            return (
              <g key={`point-${index}`}>
                {/* 数据点 */}
                <circle
                  cx={x}
                  cy={y}
                  r={selectedPoint === index ? 6 : 4}
                  fill={getConfidenceColor(point.confidence)}
                  stroke={hasBiasWarning ? "#ff6b6b" : "white"}
                  strokeWidth={hasBiasWarning ? 2 : 1}
                  className="cursor-pointer transition-all duration-200 focus:outline-none"
                  onMouseEnter={() => setSelectedPoint(index)}
                  onMouseLeave={() => setSelectedPoint(null)}
                  role="button"
                  tabIndex={0}
                  aria-label={`数据点 ${formatTime(point.timestamp)}: 数值 ${point.value}${
                    point.confidence ? `, 置信度 ${Math.round(point.confidence * 100)}%` : ''
                  }${hasBiasWarning ? ', 存在偏见预警' : ''}`}
                />
                
                {/* 偏见预警动画 */}
                {hasBiasWarning && (
                  <circle
                    cx={x}
                    cy={y}
                    r="8"
                    fill="none"
                    stroke="#ff6b6b"
                    strokeWidth="1"
                    strokeOpacity="0.5"
                    className="animate-ping pointer-events-none"
                  />
                )}
              </g>
            );
          })}
        </svg>
        
        {/* 选中点详情 */}
        {selectedPoint !== null && (
          <div 
            className="absolute bg-white dark:bg-gray-800 rounded-lg shadow-xl p-4 border border-gray-200 dark:border-gray-700 min-w-48 transform -translate-x-1/2 transition-all duration-200 z-10"
            style={{
              left: `${(selectedPoint / displayData.length) * 100}%`,
              bottom: 'calc(100% + 10px)'
            }}
          >
            <div className="text-sm space-y-2">
              <div className="font-medium text-gray-900 dark:text-white">
                {formatTime(data[selectedPoint].timestamp)}
              </div>
              <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                {data[selectedPoint].value.toLocaleString()}
              </div>
              
              {data[selectedPoint].confidence && (
                <div className="flex items-center">
                  <div 
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: getConfidenceColor(data[selectedPoint].confidence) }}
                  />
                  <span className="text-gray-600 dark:text-gray-300">
                    置信度: {Math.round(data[selectedPoint].confidence! * 100)}%
                  </span>
                </div>
              )}
              
              {data[selectedPoint].biasWarning && (
                <div className="flex items-center text-red-600 dark:text-red-400">
                  <span className="w-2 h-2 rounded-full bg-red-500 mr-2" />
                  存在偏见风险
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* 时间轴 */}
      <div className="flex justify-between mt-4 text-sm text-gray-500 dark:text-gray-400">
        {displayData.length > 0 && (
          <>
            <span>{formatTime(displayData[0].timestamp)}</span>
            <span>{formatTime(displayData[Math.floor(displayData.length / 2)].timestamp)}</span>
            <span>{formatTime(displayData[displayData.length - 1].timestamp)}</span>
          </>
        )}
      </div>
      
      {/* 无障碍提示 */}
      <div className="sr-only" aria-live="polite">
        {selectedPoint !== null 
          ? `已选中${formatTime(data[selectedPoint].timestamp)}的数据点`
          : '使用鼠标悬停或键盘导航查看详细数据'}
      </div>
      
      {/* 键盘导航提示 */}
      <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
        <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded">Tab</kbd>
        <span className="ml-2">导航数据点</span>
        <kbd className="ml-4 px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded">Enter</kbd>
        <span className="ml-2">选择数据点</span>
      </div>
    </div>
  );
};

export default TrendChart;