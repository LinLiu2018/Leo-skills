import { useState, useEffect } from 'react';
import {
  Database,
  Search,
  Plus,
  Trash2,
  Clock,
  Tag,
  Star,
  StarOff,
  Brain,
  RefreshCw,
  Filter,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import type { MemoryEntry, MemoryStats } from '../types';
import { cn } from '../utils/cn';
import { memoryApi } from '../services/api';

const categories = [
  { value: 'all', label: '全部', color: 'bg-gray-100 text-gray-700' },
  { value: 'user_profile', label: '用户资料', color: 'bg-blue-100 text-blue-700' },
  { value: 'project', label: '项目', color: 'bg-green-100 text-green-700' },
  { value: 'config', label: '配置', color: 'bg-purple-100 text-purple-700' },
  { value: 'system', label: '系统', color: 'bg-orange-100 text-orange-700' },
  { value: 'general', label: '通用', color: 'bg-gray-100 text-gray-700' },
];

// 重要性星级组件
function ImportanceStars({ level }: { level: number }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        star <= level ? (
          <Star key={star} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
        ) : (
          <StarOff key={star} className="w-4 h-4 text-gray-300" />
        )
      ))}
    </div>
  );
}

// 统计卡片
function StatCard({ title, value, icon: Icon, color }: {
  title: string;
  value: number;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-3">
        <div className={cn('p-2 rounded-lg', color)}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );
}

// 创建记忆弹窗
function CreateMemoryModal({ onClose, onSave }: { onClose: () => void; onSave: (entry: Partial<MemoryEntry>) => void }) {
  const [formData, setFormData] = useState<Partial<MemoryEntry>>({
    key: '',
    value: '',
    category: 'user_profile',
    importance: 3,
  });

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">创建新记忆</h3>

        <div className="space-y-4">
          <div>
            <label className="label">Key *</label>
            <input
              type="text"
              value={formData.key}
              onChange={(e) => setFormData({ ...formData, key: e.target.value })}
              className="input"
              placeholder="memory_key"
            />
          </div>

          <div>
            <label className="label">Value *</label>
            <textarea
              value={formData.value}
              onChange={(e) => setFormData({ ...formData, value: e.target.value })}
              className="input min-h-[100px]"
              placeholder="记忆内容..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">分类</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="input"
              >
                {categories.filter(c => c.value !== 'all').map((cat) => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="label">重要性 (1-5)</label>
              <input
                type="number"
                min={1}
                max={5}
                value={formData.importance}
                onChange={(e) => setFormData({ ...formData, importance: parseInt(e.target.value) })}
                className="input"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button onClick={onClose} className="btn-secondary">取消</button>
          <button
            onClick={() => onSave(formData)}
            className="btn-primary"
            disabled={!formData.key || !formData.value}
          >
            保存
          </button>
        </div>
      </div>
    </div>
  );
}

// 主页面
export function Memory() {
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // 从API加载记忆
  useEffect(() => {
    const fetchMemory = async () => {
      try {
        setLoading(true);
        setError(null);
        const [entriesResponse, statsResponse] = await Promise.all([
          memoryApi.getAll(),
          memoryApi.getStats(),
        ]);
        const entriesData = (entriesResponse as any).data || [];
        const statsData = (statsResponse as any).data || { total_entries: 0, categories: {}, by_importance: {} };
        setEntries(entriesData);
        setStats(statsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载记忆失败');
        console.error('Failed to fetch memory:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMemory();
  }, []);

  const filteredEntries = entries.filter((entry) => {
    const matchesSearch =
      entry.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.value.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || entry.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleDelete = (entry: MemoryEntry) => {
    if (confirm(`确定要删除记忆 "${entry.key}" 吗？`)) {
      setEntries(entries.filter((e) => e.id !== entry.id));
    }
  };

  const handleSave = (formData: Partial<MemoryEntry>) => {
    const newEntry: MemoryEntry = {
      id: Date.now().toString(),
      key: formData.key!,
      value: formData.value!,
      category: formData.category!,
      importance: formData.importance!,
      created_at: new Date().toISOString().split('T')[0],
      updated_at: new Date().toISOString().split('T')[0],
    };
    setEntries([newEntry, ...entries]);
    setShowCreateModal(false);
  };

  const handleCleanup = () => {
    if (confirm('清理过期记忆？')) {
      const now = new Date().toISOString().split('T')[0];
      setEntries(entries.filter((e) => !e.expires_at || e.expires_at > now));
    }
  };

  // 加载状态
  if (loading) {
    return (
      <div className="page-container animate-fade-in">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          <span className="ml-3 text-gray-600">加载记忆列表...</span>
        </div>
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="page-container animate-fade-in">
        <div className="card p-6 text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">加载失败</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="btn-primary">
            重新加载
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container animate-fade-in">
      {showCreateModal && (
        <CreateMemoryModal onClose={() => setShowCreateModal(false)} onSave={handleSave} />
      )}

      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h1 className="page-title">共享记忆</h1>
          <p className="page-description">跨会话持久化的用户偏好、项目上下文等信息</p>
        </div>
        <div className="flex gap-3">
          <button onClick={handleCleanup} className="btn-secondary">
            <RefreshCw className="w-4 h-4 mr-2" />
            清理过期
          </button>
          <button onClick={() => setShowCreateModal(true)} className="btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            添加记忆
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <StatCard
          title="总条目"
          value={stats?.total_entries || entries.length}
          icon={Database}
          color="bg-primary-500"
        />
        {categories.filter(c => c.value !== 'all').map((cat) => (
          <StatCard
            key={cat.value}
            title={cat.label}
            value={stats?.categories[cat.value] || 0}
            icon={Tag}
            color={cat.color.replace('bg-', 'bg-opacity-100 bg-')}
          />
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索记忆..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="flex gap-2">
          {categories.map((cat) => (
            <button
              key={cat.value}
              onClick={() => setSelectedCategory(cat.value)}
              className={cn(
                'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                selectedCategory === cat.value
                  ? cat.color
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              )}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Key</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">分类</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">重要性</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">更新于</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredEntries.map((entry) => {
                const category = categories.find(c => c.value === entry.category);
                return (
                  <tr key={entry.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Brain className="w-4 h-4 text-primary-500" />
                        <span className="font-medium text-gray-900">{entry.key}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-600 max-w-md truncate" title={entry.value}>
                        {entry.value}
                      </p>
                    </td>
                    <td className="px-6 py-4">
                      {category && (
                        <span className={cn('px-2 py-1 rounded-full text-xs font-medium', category.color)}>
                          {category.label}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <ImportanceStars level={entry.importance} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {entry.updated_at}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleDelete(entry)}
                          className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
