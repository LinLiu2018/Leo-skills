import { useState, useEffect } from 'react';
import {
  Users,
  Plus,
  Search,
  Bot,
  Brain,
  Code,
  Palette,
  BarChart3,
  Globe,
  FileText,
  Sparkles,
  Edit,
  Trash2,
  CheckCircle2,
  XCircle,
  ArrowLeft,
  Save,
  X,
  Wrench,
  Loader2,
  AlertCircle,
  Play,
  MessageSquare,
  Send,
  Info,
  Lightbulb,
  Target,
  BookOpen,
  Zap,
} from 'lucide-react';
import type { Agent } from '../types';
import { cn } from '../utils/cn';
import { agentsApi, intentApi } from '../services/api';

// Agent 角色配置
const agentRoles = [
  { value: 'researcher', label: '研究员', icon: Globe, color: 'bg-blue-500' },
  { value: 'creator', label: '创意设计师', icon: Palette, color: 'bg-purple-500' },
  { value: 'developer', label: '代码助手', icon: Code, color: 'bg-green-500' },
  { value: 'analyst', label: '数据分析师', icon: BarChart3, color: 'bg-orange-500' },
  { value: 'assistant', label: '通用助手', icon: Bot, color: 'bg-gray-500' },
];

// 状态标签组件
function StatusBadge({ status }: { status: Agent['status'] }) {
  const config = {
    active: { icon: CheckCircle2, className: 'bg-green-100 text-green-700', label: '运行中' },
    inactive: { icon: XCircle, className: 'bg-gray-100 text-gray-600', label: '已停用' },
    error: { icon: XCircle, className: 'bg-red-100 text-red-700', label: '错误' },
  };
  const { icon: Icon, className, label } = config[status];

  return (
    <span className={cn('inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium', className)}>
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
}

// Agent 执行器组件
function AgentExecutor({ agent, onClose }: { agent: Agent; onClose: () => void }) {
  const [message, setMessage] = useState('');
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [showHelp, setShowHelp] = useState(true);

  const role = agentRoles.find(r => r.value === agent.role);
  const RoleIcon = role?.icon || Bot;

  // 生成自然语言描述
  const getNaturalDescription = () => {
    const roleLabel = role?.label || agent.role;
    const capabilitiesText = agent.capabilities.length > 0
      ? `我擅长${agent.capabilities.slice(0, 3).join('、')}等工作。`
      : '';
    const skillsText = agent.skills.length > 0
      ? `我可以使用 ${agent.skills.slice(0, 3).join('、')} 等技能来帮助你。`
      : '';

    return {
      intro: `你好！我是 ${agent.display_name}，一个${roleLabel}。`,
      description: agent.description || '',
      capabilities: capabilitiesText,
      skills: skillsText,
      examples: generateExamples(),
    };
  };

  // 生成使用示例
  const generateExamples = () => {
    const examples: string[] = [];
    if (agent.capabilities.length > 0) {
      const cap = agent.capabilities[0];
      examples.push(`帮我${cap}关于...`);
      examples.push(`请为我${cap}...`);
    }
    if (agent.role === 'researcher') {
      examples.push('研究一下量子计算的最新进展');
      examples.push('帮我调研一下房地产市场的趋势');
    } else if (agent.role === 'creator') {
      examples.push('帮我写一份产品推广文案');
      examples.push('为我的新公司设计一个Logo方案');
    } else if (agent.role === 'developer') {
      examples.push('帮我写一个Python脚本处理Excel文件');
      examples.push('优化这段代码的性能');
    } else if (agent.role === 'analyst') {
      examples.push('分析这份销售数据并生成报告');
      examples.push('帮我统计一下用户行为数据');
    }
    return examples.slice(0, 3);
  };

  const handleExecute = async () => {
    if (!message.trim()) return;

    try {
      setExecuting(true);
      setError(null);
      setResult(null);
      setShowHelp(false);

      // 调用 Agent 执行 API
      const response = await agentsApi.execute(agent.id, message);
      const data = (response as any).data;

      setResult({
        agent: data.agent_name,
        role: data.role,
        task: data.task,
        response: data.response,
        execution_time_ms: data.execution_time_ms,
        capabilities_used: data.capabilities_used,
        status: data.status,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '执行失败');
    } finally {
      setExecuting(false);
    }
  };

  const description = getNaturalDescription();

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gray-50">
          <div className="flex items-center gap-3">
            <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', role?.color || 'bg-gray-500')}>
              <RoleIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-gray-900">{agent.display_name}</h2>
              <p className="text-sm text-gray-500">{role?.label || agent.role}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowHelp(!showHelp)}
              className={cn(
                "p-2 rounded-lg transition-colors",
                showHelp ? "bg-primary-100 text-primary-600" : "hover:bg-gray-200 text-gray-500"
              )}
              title="显示/隐藏帮助"
            >
              <BookOpen className="w-5 h-5" />
            </button>
            <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          <div className="space-y-4">
            {/* 自然语言描述区域 */}
            {showHelp && (
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-100">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg shrink-0">
                    <Bot className="w-5 h-5 text-purple-600" />
                  </div>
                  <div className="space-y-3 flex-1">
                    <div>
                      <h3 className="font-medium text-gray-900 mb-1">自我介绍</h3>
                      <p className="text-sm text-gray-600">{description.intro}</p>
                      {description.description && (
                        <p className="text-sm text-gray-600 mt-1">{description.description}</p>
                      )}
                    </div>

                    {description.capabilities && (
                      <div className="flex items-start gap-2">
                        <Zap className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                        <p className="text-sm text-gray-600">{description.capabilities}</p>
                      </div>
                    )}

                    {description.skills && (
                      <div className="flex items-start gap-2">
                        <Target className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
                        <p className="text-sm text-gray-600">{description.skills}</p>
                      </div>
                    )}

                    {description.examples.length > 0 && (
                      <div className="mt-3 p-3 bg-white/60 rounded-lg border border-purple-100">
                        <p className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
                          <Lightbulb className="w-3 h-3" />
                          你可以这样对我说
                        </p>
                        <div className="space-y-1.5">
                          {description.examples.map((example, i) => (
                            <button
                              key={i}
                              onClick={() => setMessage(example)}
                              className="block w-full text-left px-3 py-2 bg-white text-sm rounded border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors text-gray-700"
                            >
                              &quot;{example}&quot;
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Agent 信息 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-700">能力标签</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {agent.capabilities.map((cap, i) => (
                  <span key={i} className="px-2 py-1 bg-white text-gray-600 text-xs rounded border">
                    {cap}
                  </span>
                ))}
                {agent.capabilities.length === 0 && (
                  <span className="text-sm text-gray-400">暂无能力标签</span>
                )}
              </div>
            </div>

            {/* 消息输入 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <MessageSquare className="w-4 h-4 inline mr-1" />
                发送任务给 Agent
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleExecute()}
                  placeholder={`例如: 帮我${agent.capabilities[0] || '完成任务'}...`}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                <button
                  onClick={handleExecute}
                  disabled={executing || !message.trim()}
                  className="btn-primary flex items-center gap-2"
                >
                  {executing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  发送
                </button>
              </div>
            </div>

            {/* 执行结果 */}
            {(result || error) && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">执行结果</label>
                {error ? (
                  <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-600">
                    {error}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Agent 回复内容 */}
                    <div className="p-4 rounded-lg bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-100">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={cn('w-6 h-6 rounded flex items-center justify-center', role?.color || 'bg-gray-500')}>
                          <RoleIcon className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-sm font-medium text-gray-700">{result.agent}</span>
                        <span className="text-xs text-gray-400 ml-auto">{result.execution_time_ms}ms</span>
                      </div>
                      <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                        {result.response}
                      </div>
                    </div>

                    {/* 技术详情（可折叠） */}
                    <details className="text-xs">
                      <summary className="text-gray-500 cursor-pointer hover:text-gray-700">查看技术详情</summary>
                      <pre className="mt-2 p-3 bg-gray-100 rounded-lg text-gray-600 overflow-auto max-h-32">
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </details>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Agent 卡片组件
function AgentCard({ agent, onEdit, onDelete, onExecute }: {
  agent: Agent;
  onEdit: (agent: Agent) => void;
  onDelete: (agent: Agent) => void;
  onExecute: (agent: Agent) => void;
}) {
  const role = agentRoles.find(r => r.value === agent.role);
  const RoleIcon = role?.icon || Bot;

  return (
    <div className="card p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center', role?.color || 'bg-gray-500')}>
            <RoleIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{agent.display_name}</h3>
            <p className="text-sm text-gray-500">{agent.name}</p>
          </div>
        </div>
        <StatusBadge status={agent.status} />
      </div>

      <p className="text-sm text-gray-600 mb-4 line-clamp-2">{agent.description}</p>

      <div className="mb-4">
        <p className="text-xs text-gray-500 mb-2">能力 ({agent.capabilities.length})</p>
        <div className="flex flex-wrap gap-1">
          {agent.capabilities.slice(0, 4).map((cap, i) => (
            <span key={i} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
              {cap}
            </span>
          ))}
          {agent.capabilities.length > 4 && (
            <span className="px-2 py-1 text-gray-400 text-xs">+{agent.capabilities.length - 4}</span>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="text-xs text-gray-400">
          关联 Skills: {agent.skills.length}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onExecute(agent)}
            className="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
            title="执行"
          >
            <Play className="w-4 h-4" />
          </button>
          <button
            onClick={() => onEdit(agent)}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(agent)}
            className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

// Agent 表单组件
function AgentForm({ agent, onSave, onCancel }: {
  agent?: Agent;
  onSave: (agent: Agent) => void;
  onCancel: () => void;
}) {
  const [formData, setFormData] = useState<Partial<Agent>>(agent || {
    name: '',
    display_name: '',
    description: '',
    role: 'assistant',
    capabilities: [],
    skills: [],
    status: 'active',
  });

  const [newCapability, setNewCapability] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData as Agent);
  };

  const addCapability = () => {
    if (newCapability && !formData.capabilities?.includes(newCapability)) {
      setFormData({
        ...formData,
        capabilities: [...(formData.capabilities || []), newCapability],
      });
      setNewCapability('');
    }
  };

  const removeCapability = (cap: string) => {
    setFormData({
      ...formData,
      capabilities: formData.capabilities?.filter(c => c !== cap) || [],
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="label">名称 *</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="input"
            placeholder="agent_name"
            required
          />
        </div>
        <div>
          <label className="label">显示名称 *</label>
          <input
            type="text"
            value={formData.display_name}
            onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
            className="input"
            placeholder="代理显示名称"
            required
          />
        </div>
      </div>

      <div>
        <label className="label">角色 *</label>
        <div className="grid grid-cols-5 gap-3">
          {agentRoles.map((role) => {
            const Icon = role.icon;
            return (
              <button
                key={role.value}
                type="button"
                onClick={() => setFormData({ ...formData, role: role.value })}
                className={cn(
                  'p-4 rounded-lg border-2 transition-all text-center',
                  formData.role === role.value
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <Icon className={cn('w-6 h-6 mx-auto mb-2', role.color.replace('bg-', 'text-'))} />
                <span className="text-sm font-medium">{role.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <label className="label">描述</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="input min-h-[100px]"
          placeholder="代理描述..."
        />
      </div>

      <div>
        <label className="label">能力</label>
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={newCapability}
            onChange={(e) => setNewCapability(e.target.value)}
            className="input flex-1"
            placeholder="添加能力..."
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCapability())}
          />
          <button
            type="button"
            onClick={addCapability}
            className="btn-primary"
          >
            添加
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {formData.capabilities?.map((cap) => (
            <span key={cap} className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
              {cap}
              <button type="button" onClick={() => removeCapability(cap)} className="hover:text-primary-900">
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t">
        <button type="button" onClick={onCancel} className="btn-secondary">
          <X className="w-4 h-4 mr-2" />
          取消
        </button>
        <button type="submit" className="btn-primary">
          <Save className="w-4 h-4 mr-2" />
          保存
        </button>
      </div>
    </form>
  );
}

// 主页面
export function Agents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [view, setView] = useState<'grid' | 'form'>('grid');
  const [editingAgent, setEditingAgent] = useState<Agent | undefined>();
  const [executingAgent, setExecutingAgent] = useState<Agent | null>(null);

  // 从API加载代理
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await agentsApi.getAll();
        const data = (response as any).data || [];
        setAgents(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载代理失败');
        console.error('Failed to fetch agents:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  const filteredAgents = agents.filter((agent) =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.display_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreate = () => {
    setEditingAgent(undefined);
    setView('form');
  };

  const handleEdit = (agent: Agent) => {
    setEditingAgent(agent);
    setView('form');
  };

  const handleDelete = (agent: Agent) => {
    if (confirm(`确定要删除代理 "${agent.display_name}" 吗？`)) {
      setAgents(agents.filter((a) => a.id !== agent.id));
    }
  };

  const handleSave = (agentData: Agent) => {
    if (editingAgent) {
      setAgents(agents.map((a) => (a.id === editingAgent.id ? { ...agentData, id: a.id } : a)));
    } else {
      const newAgent: Agent = {
        ...agentData,
        id: Date.now().toString(),
        created_at: new Date().toISOString().split('T')[0],
        updated_at: new Date().toISOString().split('T')[0],
      };
      setAgents([...agents, newAgent]);
    }
    setView('grid');
  };

  const handleExecute = (agent: Agent) => {
    setExecutingAgent(agent);
  };

  // 加载状态
  if (loading) {
    return (
      <div className="page-container animate-fade-in">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          <span className="ml-3 text-gray-600">加载代理列表...</span>
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

  if (view === 'form') {
    return (
      <div className="page-container">
        <button
          onClick={() => setView('grid')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          返回列表
        </button>
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            {editingAgent ? '编辑 Agent' : '创建新 Agent'}
          </h2>
          <AgentForm
            agent={editingAgent}
            onSave={handleSave}
            onCancel={() => setView('grid')}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="page-container animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h1 className="page-title">Agents 管理</h1>
          <p className="page-description">配置和管理系统中的智能代理</p>
        </div>
        <button onClick={handleCreate} className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          创建 Agent
        </button>
      </div>

      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索 agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
        <div className="card p-4">
          <p className="text-sm text-gray-500">总 Agents</p>
          <p className="text-2xl font-bold text-gray-900">{agents.length}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">运行中</p>
          <p className="text-2xl font-bold text-green-600">
            {agents.filter((a) => a.status === 'active').length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">研究员</p>
          <p className="text-2xl font-bold text-blue-600">
            {agents.filter((a) => a.role === 'researcher').length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">创意设计师</p>
          <p className="text-2xl font-bold text-purple-600">
            {agents.filter((a) => a.role === 'creator').length}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onExecute={handleExecute}
          />
        ))}
      </div>

      {/* Agent 执行器 */}
      {executingAgent && (
        <AgentExecutor
          agent={executingAgent}
          onClose={() => setExecutingAgent(null)}
        />
      )}
    </div>
  );
}
