import { useEffect } from 'react';
import {
  Wrench,
  Users,
  Workflow,
  Database,
  Activity,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Sparkles,
  GitBranch,
  Terminal,
} from 'lucide-react';
import { useAppStore } from '../store/appStore';

// 统计卡片组件
function StatCard({
  title,
  value,
  icon: Icon,
  change,
  changeType,
  color,
}: {
  title: string;
  value: number | string;
  icon: React.ElementType;
  change?: string;
  changeType?: 'up' | 'down' | 'neutral';
  color: string;
}) {
  return (
    <div className="card p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {change && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${
              changeType === 'up' ? 'text-green-600' :
              changeType === 'down' ? 'text-red-600' : 'text-gray-500'
            }`}>
              {changeType === 'up' && <ArrowUpRight className="w-4 h-4" />}
              {changeType === 'down' && <ArrowDownRight className="w-4 h-4" />}
              <span>{change}</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
}

// 快速操作组件
function QuickAction({
  icon: Icon,
  label,
  description,
  onClick,
  color,
}: {
  icon: React.ElementType;
  label: string;
  description: string;
  onClick: () => void;
  color: string;
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-start gap-4 p-4 bg-white border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-sm transition-all text-left w-full"
    >
      <div className={`p-2 rounded-lg ${color}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <h3 className="font-medium text-gray-900">{label}</h3>
        <p className="text-sm text-gray-500 mt-1">{description}</p>
      </div>
    </button>
  );
}

// 活动日志组件
function ActivityLog() {
  const activities = [
    { id: 1, action: '执行了数据分析工作流', time: '5分钟前', type: 'workflow' },
    { id: 2, action: '新增了技能：web_search', time: '1小时前', type: 'skill' },
    { id: 3, action: 'Agent research_agent 完成研究任务', time: '2小时前', type: 'agent' },
    { id: 4, action: '系统完成自动备份', time: '6小时前', type: 'system' },
  ];

  const getIcon = (type: string) => {
    switch (type) {
      case 'workflow': return Workflow;
      case 'skill': return Wrench;
      case 'agent': return Users;
      default: return Activity;
    }
  };

  return (
    <div className="card">
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">最近活动</h3>
      </div>
      <div className="divide-y divide-gray-100">
        {activities.map((activity) => {
          const Icon = getIcon(activity.type);
          return (
            <div key={activity.id} className="p-4 flex items-center gap-3">
              <div className="p-2 bg-gray-50 rounded-lg">
                <Icon className="w-4 h-4 text-gray-500" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">{activity.action}</p>
              </div>
              <span className="text-xs text-gray-500">{activity.time}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// 分类统计组件
function CategoryStats() {
  const stats = [
    { name: 'AI', count: 8, color: 'bg-blue-500' },
    { name: '内容', count: 6, color: 'bg-green-500' },
    { name: '数据', count: 5, color: 'bg-purple-500' },
    { name: '开发', count: 7, color: 'bg-orange-500' },
    { name: '媒体', count: 4, color: 'bg-pink-500' },
  ];

  const total = stats.reduce((sum, s) => sum + s.count, 0);

  return (
    <div className="card">
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">技能分类分布</h3>
      </div>
      <div className="p-4 space-y-4">
        {stats.map((stat) => (
          <div key={stat.name} className="flex items-center gap-4">
            <div className={`w-3 h-3 rounded-full ${stat.color}`} />
            <div className="flex-1">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">{stat.name}</span>
                <span className="text-sm font-medium text-gray-900">{stat.count}</span>
              </div>
              <div className="mt-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full ${stat.color} rounded-full transition-all duration-500`}
                  style={{ width: `${(stat.count / total) * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// 主页面
export function Dashboard() {
  const { stats, refreshStats, isLoading } = useAppStore();

  useEffect(() => {
    refreshStats();
  }, [refreshStats]);

  return (
    <div className="page-container animate-fade-in">
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">仪表盘</h1>
        <p className="page-description">
          欢迎使用 Leo AI System，这里是系统的概览和控制中心
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Skills"
          value={stats?.total_skills || 45}
          icon={Wrench}
          change="+3 本周"
          changeType="up"
          color="bg-blue-500"
        />
        <StatCard
          title="Agents"
          value={stats?.total_agents || 9}
          icon={Users}
          change="+1 本周"
          changeType="up"
          color="bg-green-500"
        />
        <StatCard
          title="Workflows"
          value={stats?.total_workflows || 12}
          icon={Workflow}
          change="稳定"
          changeType="neutral"
          color="bg-purple-500"
        />
        <StatCard
          title="记忆条目"
          value={stats?.memory_entries || 28}
          icon={Database}
          change="+12 本周"
          changeType="up"
          color="bg-orange-500"
        />
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">快速操作</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <QuickAction
            icon={Sparkles}
            label="创建新 Skill"
            description="快速定义和配置新技能"
            onClick={() => window.location.href = '/skills/new'}
            color="bg-primary-500"
          />
          <QuickAction
            icon={Terminal}
            label="调试意图识别"
            description="测试和优化意图识别引擎"
            onClick={() => window.location.href = '/intent'}
            color="bg-indigo-500"
          />
          <QuickAction
            icon={GitBranch}
            label="新建工作流"
            description="编排多步骤任务流程"
            onClick={() => window.location.href = '/workflows/new'}
            color="bg-cyan-500"
          />
          <QuickAction
            icon={Zap}
            label="执行能力索引"
            description="更新技能和代理索引"
            onClick={() => console.log('更新索引')}
            color="bg-amber-500"
          />
        </div>
      </div>

      {/* Bottom Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ActivityLog />
        </div>
        <div>
          <CategoryStats />
        </div>
      </div>

      {/* System Status */}
      <div className="mt-8 card p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">系统状态</h3>
              <p className="text-sm text-gray-500">所有服务正常运行</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>运行时间: {stats?.uptime_hours || 168} 小时</span>
          </div>
        </div>
      </div>
    </div>
  );
}
