import { useState } from 'react'
import DashboardLayout, { DashboardModule } from './components/DashboardLayout'
import TrendChart from './components/TrendChart'
import AgentStatusCard from './components/AgentStatusCard'

const sampleTrendData = [
  { timestamp: '2024-01-01T08:00:00', value: 150, confidence: 0.9 },
  { timestamp: '2024-01-01T09:00:00', value: 230, confidence: 0.8 },
  { timestamp: '2024-01-01T10:00:00', value: 180, confidence: 0.7 },
  { timestamp: '2024-01-01T11:00:00', value: 320, confidence: 0.6 },
  { timestamp: '2024-01-01T12:00:00', value: 280, confidence: 0.5 },
  { timestamp: '2024-01-01T13:00:00', value: 400, confidence: 0.4, biasWarning: true },
  { timestamp: '2024-01-01T14:00:00', value: 350, confidence: 0.7 },
  { timestamp: '2024-01-01T15:00:00', value: 420, confidence: 0.8 },
];

function App() {
  return (
    <DashboardLayout userRole="analyst">
      {/* Top Cards for Agents */}
      <DashboardModule colSpan={12} title="智能体协作网络">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <AgentStatusCard agentName="数据分析助手" status="online" confidence={0.92} lastSync="刚刚" />
            <AgentStatusCard agentName="代码生成助手" status="busy" confidence={0.88} lastSync="1分钟前" />
            <AgentStatusCard agentName="安全审计员" status="online" confidence={0.99} isEdgeDevice={true} />
            <AgentStatusCard agentName="预测模型" status="offline" confidence={0.0} lastSync="1天前" />
        </div>
      </DashboardModule>

      {/* Main Chart */}
      <DashboardModule colSpan={8} rowSpan={2} title="全系统负载趋势 (Aura预测)">
        <div className="h-full min-h-[300px]">
             <TrendChart data={sampleTrendData} title="实时负载" className="h-full" />
        </div>
      </DashboardModule>

      {/* Side Panel 1 */}
      <DashboardModule colSpan={4} title="决策透明度">
        <div className="space-y-4">
             <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <h4 className="font-bold text-green-800">系统运行正常</h4>
                <p className="text-sm text-green-700">所有伦理护栏已激活。未检测到高风险偏见。</p>
             </div>
             <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-bold text-blue-800">边缘节点在线</h4>
                <p className="text-sm text-blue-700">3个边缘节点正在处理本地推理任务。</p>
             </div>
        </div>
      </DashboardModule>
      
      {/* Side Panel 2 */}
      <DashboardModule colSpan={4} title="快速操作">
        <div className="grid grid-cols-2 gap-2">
            <button className="p-3 bg-gray-100 rounded hover:bg-gray-200 text-sm">生成月报</button>
            <button className="p-3 bg-gray-100 rounded hover:bg-gray-200 text-sm">系统自检</button>
            <button className="p-3 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 col-span-2 font-bold text-sm">启动新任务</button>
        </div>
      </DashboardModule>

    </DashboardLayout>
  )
}

export default App
