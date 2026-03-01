import { useState } from 'react';
import {
  Zap,
  Sparkles,
  TrendingUp,
  GitCommit,
  Clock,
  CheckCircle2,
  XCircle,
  Play,
  Pause,
  RotateCw,
  Lightbulb,
  Target,
  Code,
} from 'lucide-react';
import { cn } from '../utils/cn';

// 技能进化任务
interface EvolutionTask {
  id: string;
  skill_name: string;
  type: 'improvement' | 'bugfix' | 'feature';
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

const mockTasks: EvolutionTask[] = [
  {
    id: '1',
    skill_name: 'web_search_skill',
    type: 'improvement',
    description: '优化搜索结果相关性排序算法',
    status: 'completed',
    progress: 100,
    created_at: '2024-02-01',
    started_at: '2024-02-01',
    completed_at: '2024-02-02',
  },
  {
    id: '2',
    skill_name: 'document_analysis_skill',
    type: 'feature',
    description: '添加PDF文档支持',
    status: 'running',
    progress: 65,
    created_at: '2024-02-03',
    started_at: '2024-02-03',
  },
  {
    id: '3',
    skill_name: 'video_editing_skill',
    type: 'bugfix',
    description: '修复剪辑后音频丢失问题',
    status: 'pending',
    progress: 0,
    created_at: '2024-02-04',
  },
];

// 类型配置
const typeConfig = {
  improvement: { label: '优化', color: 'bg-blue-100 text-blue-700', icon: TrendingUp },
  bugfix: { label: '修复', color: 'bg-red-100 text-red-700', icon: Target },
  feature: { label: '新功能', color: 'bg-green-100 text-green-700', icon: Lightbulb },
};

// 状态配置
const statusConfig = {
  pending: { label: '等待中', color: 'text-gray-500', icon: Clock },
  running: { label: '运行中', color: 'text-primary-600', icon: RotateCw },
  completed: { label: '已完成', color: 'text-green-600', icon: CheckCircle2 },
  failed: { label: '失败', color: 'text-red-600', icon: XCircle },
};

function TaskCard({ task }: { task: EvolutionTask }) {
  const type = typeConfig[task.type];
  const status = statusConfig[task.status];
  const TypeIcon = type.icon;
  const StatusIcon = status.icon;

  return (
    <div className="card p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn('p-2 rounded-lg', type.color)}>
            <TypeIcon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{task.skill_name}</h3>
            <span className={cn('text-sm', status.color)}>
              <StatusIcon className="w-4 h-4 inline mr-1" />
              {status.label}
            </span>
          </div>
        </div>
        <span className={cn('px-2 py-1 rounded-full text-xs font-medium', type.color)}>
          {type.label}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-4">{task.description}</p>

      {task.status === 'running' && (
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-500">进度</span>
            <span className="font-medium">{task.progress}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 rounded-full transition-all duration-500"
              style={{ width: `${task.progress}%` }}
            />
          </div>
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>创建于: {task.created_at}</span>
        {task.completed_at && <span>完成于: {task.completed_at}</span>}
      </div>
    </div>
  );
}

export function Evolution() {
  const [tasks, setTasks] = useState<EvolutionTask[]>(mockTasks);
  const [filter, setFilter] = useState<EvolutionTask['status'] | 'all'>('all');

  const filteredTasks = filter === 'all'
    ? tasks
    : tasks.filter(t => t.status === filter);

  const stats = {
    total: tasks.length,
    pending: tasks.filter(t => t.status === 'pending').length,
    running: tasks.filter(t => t.status === 'running').length,
    completed: tasks.filter(t => t.status === 'completed').length,
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h1 className="page-title">技能进化</h1>
          <p className="page-description">自动化技能改进和优化系统</p>
        </div>
        <button className="btn-primary">
          <Sparkles className="w-4 h-4 mr-2" />
          创建进化任务
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="card p-4">
          <p className="text-sm text-gray-500">总任务</p>
          <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">等待中</p>
          <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">运行中</p>
          <p className="text-2xl font-bold text-primary-600">{stats.running}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">已完成</p>
          <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {(['all', 'pending', 'running', 'completed', 'failed'] as const).map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              filter === s
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            )}
          >
            {s === 'all' ? '全部' : statusConfig[s].label}
          </button>
        ))}
      </div>

      {/* Tasks */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTasks.map((task) => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
    </div>
  );
}
