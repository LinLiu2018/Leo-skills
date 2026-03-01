import { useState, useEffect } from 'react';
import {
  Wrench,
  Plus,
  Search,
  Filter,
  MoreVertical,
  Play,
  Edit,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ArrowLeft,
  Save,
  X,
  Code,
  FileText,
  Loader2,
  Terminal,
  ChevronDown,
  Info,
  Lightbulb,
  Zap,
  BookOpen,
} from 'lucide-react';
import type { Skill, SkillCategory } from '../types';
import { cn } from '../utils/cn';
import { skillsApi, type SkillMethod } from '../services/api';

// 分类标签映射
const categoryLabels: Record<string, string> = {
  'automation': '自动化',
  'backend': '后端',
  'business': '业务',
  'collaboration': '协作',
  'content_creation': '内容创作',
  'core': '核心',
  'debugging': '调试',
  'development': '开发',
  'devops': '运维',
  'frontend': '前端',
  'intelligence': '智能',
};

// 状态标签组件
function StatusBadge({ status }: { status: Skill['status'] }) {
  const config = {
    active: { icon: CheckCircle2, className: 'bg-green-100 text-green-700', label: '运行中' },
    inactive: { icon: XCircle, className: 'bg-gray-100 text-gray-600', label: '已停用' },
    error: { icon: AlertCircle, className: 'bg-red-100 text-red-700', label: '错误' },
  };
  const { icon: Icon, className, label } = config[status];

  return (
    <span className={cn('inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium', className)}>
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
}

// 技能执行组件
function SkillExecutor({ skill, onClose }: { skill: Skill; onClose: () => void }) {
  const [methods, setMethods] = useState<SkillMethod[]>([]);
  const [selectedMethod, setSelectedMethod] = useState<string>('');
  const [params, setParams] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const [showHelp, setShowHelp] = useState(true);

  // 加载技能方法
  useEffect(() => {
    const fetchMethods = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await skillsApi.getMethods(skill.id);
        const data = (response as any).data || [];
        // 过滤掉内部方法
        const publicMethods = data.filter((m: SkillMethod) =>
          !m.name.startsWith('_') &&
          !['get_help', 'evolve', 'get_evolution_history'].includes(m.name)
        );
        setMethods(publicMethods);
        if (publicMethods.length > 0) {
          setSelectedMethod(publicMethods[0].name);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载方法失败');
      } finally {
        setLoading(false);
      }
    };
    fetchMethods();
  }, [skill.id]);

  // 获取当前选中方法的参数
  const currentMethod = methods.find(m => m.name === selectedMethod);

  // 生成自然语言描述
  const getNaturalDescription = () => {
    const categoryLabel = categoryLabels[skill.category.split('/')[0]] || skill.category;
    const triggerText = skill.triggers.length > 0
      ? `你可以通过说"${skill.triggers.slice(0, 3).join('"、"')}"等关键词来触发此技能。`
      : '';

    return {
      intro: `${skill.display_name} 是一个${categoryLabel}类技能，${skill.description || '用于执行特定任务'}。`,
      triggers: triggerText,
      usage: currentMethod
        ? `当前选择的方法 "${currentMethod.name}" ${currentMethod.doc?.split('\n')[0] || '可以执行相关操作'}。`
        : '请选择一个方法来执行。',
      example: generateExample(),
    };
  };

  // 生成使用示例
  const generateExample = () => {
    if (!currentMethod) return null;
    const exampleParams: Record<string, string> = {};
    currentMethod.params.forEach(p => {
      if (p.type.includes('str')) {
        exampleParams[p.name] = p.default || `示例${p.name}`;
      } else if (p.type.includes('int') || p.type.includes('float')) {
        exampleParams[p.name] = p.default || '10';
      } else if (p.type.includes('bool')) {
        exampleParams[p.name] = p.default || 'true';
      } else {
        exampleParams[p.name] = p.default || `<${p.name}>`;
      }
    });
    return exampleParams;
  };

  // 执行技能
  const handleExecute = async () => {
    if (!selectedMethod) return;

    try {
      setExecuting(true);
      setError(null);
      setResult(null);
      setShowHelp(false);

      // 转换参数类型
      const convertedParams: Record<string, unknown> = {};
      if (currentMethod) {
        for (const param of currentMethod.params) {
          const value = params[param.name];
          if (value !== undefined && value !== '') {
            // 尝试解析 JSON，否则保持字符串
            try {
              convertedParams[param.name] = JSON.parse(value);
            } catch {
              convertedParams[param.name] = value;
            }
          }
        }
      }

      const response = await skillsApi.execute(skill.id, selectedMethod, convertedParams);
      setResult((response as any).data?.result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '执行失败');
    } finally {
      setExecuting(false);
    }
  };

  const description = getNaturalDescription();

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gray-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Terminal className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h2 className="font-bold text-gray-900">{skill.display_name}</h2>
              <p className="text-sm text-gray-500">{skill.name}</p>
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
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
              <span className="ml-2 text-gray-600">加载方法列表...</span>
            </div>
          ) : error && !result ? (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-600">{error}</p>
            </div>
          ) : methods.length === 0 ? (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
              <p className="text-gray-600">该技能没有可执行的方法</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* 自然语言描述区域 */}
              {showHelp && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg shrink-0">
                      <Info className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="space-y-3 flex-1">
                      <div>
                        <h3 className="font-medium text-gray-900 mb-1">关于此技能</h3>
                        <p className="text-sm text-gray-600">{description.intro}</p>
                      </div>

                      {description.triggers && (
                        <div className="flex items-start gap-2">
                          <Zap className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                          <p className="text-sm text-gray-600">{description.triggers}</p>
                        </div>
                      )}

                      <div className="flex items-start gap-2">
                        <Lightbulb className="w-4 h-4 text-green-500 mt-0.5 shrink-0" />
                        <p className="text-sm text-gray-600">{description.usage}</p>
                      </div>

                      {description.example && Object.keys(description.example).length > 0 && (
                        <div className="mt-3 p-3 bg-white/60 rounded-lg border border-blue-100">
                          <p className="text-xs font-medium text-gray-500 mb-2">示例参数</p>
                          <div className="flex flex-wrap gap-2">
                            {Object.entries(description.example).map(([key, value]) => (
                              <button
                                key={key}
                                onClick={() => setParams({ ...params, [key]: value })}
                                className="px-2 py-1 bg-white text-xs rounded border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
                              >
                                {key}: <span className="text-primary-600">{value}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* 方法选择 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">选择方法</label>
                <div className="relative">
                  <select
                    value={selectedMethod}
                    onChange={(e) => {
                      setSelectedMethod(e.target.value);
                      setParams({});
                      setResult(null);
                      setError(null);
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 appearance-none bg-white"
                  >
                    {methods.map((method) => (
                      <option key={method.name} value={method.name}>
                        {method.name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
                {currentMethod?.doc && (
                  <p className="mt-2 text-sm text-gray-500">{currentMethod.doc.split('\n')[0]}</p>
                )}
              </div>

              {/* 参数输入 */}
              {currentMethod && currentMethod.params.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">参数</label>
                  <div className="space-y-3">
                    {currentMethod.params.map((param) => (
                      <div key={param.name} className="flex flex-col">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-gray-700">{param.name}</span>
                          {param.required && <span className="text-red-500 text-xs">*必填</span>}
                          <span className="text-xs text-gray-400">({param.type})</span>
                        </div>
                        <input
                          type="text"
                          value={params[param.name] || ''}
                          onChange={(e) => setParams({ ...params, [param.name]: e.target.value })}
                          placeholder={param.default ? `默认: ${param.default}` : `输入 ${param.name}`}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 执行按钮 */}
              <div className="flex justify-end">
                <button
                  onClick={handleExecute}
                  disabled={executing || !selectedMethod}
                  className="btn-primary flex items-center gap-2"
                >
                  {executing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      执行中...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      执行
                    </>
                  )}
                </button>
              </div>

              {/* 执行结果 */}
              {(result !== null || error) && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">执行结果</label>
                  <div className={cn(
                    "p-4 rounded-lg font-mono text-sm overflow-auto max-h-96",
                    error ? "bg-red-50 border border-red-200" : "bg-gray-900 text-green-400"
                  )}>
                    {error ? (
                      <span className="text-red-600">{error}</span>
                    ) : (
                      <pre className="whitespace-pre-wrap">
                        {typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result)}
                      </pre>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Skill 表单组件
function SkillForm({ skill, onSave, onCancel }: { skill?: Skill; onSave: (skill: Skill) => void; onCancel: () => void }) {
  const [formData, setFormData] = useState<Partial<Skill>>(skill || {
    name: '',
    display_name: '',
    version: '1.0.0',
    category: 'tools',
    description: '',
    author: '',
    status: 'active',
    triggers: [],
    inputs: [],
    outputs: [],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData as Skill);
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
            placeholder="skill_name"
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
            placeholder="技能显示名称"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="label">版本</label>
          <input
            type="text"
            value={formData.version}
            onChange={(e) => setFormData({ ...formData, version: e.target.value })}
            className="input"
            placeholder="1.0.0"
          />
        </div>
        <div>
          <label className="label">分类 *</label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value as SkillCategory })}
            className="input"
            required
          >
            {Object.entries(categoryLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="label">描述</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="input min-h-[100px]"
          placeholder="技能描述..."
        />
      </div>

      <div>
        <label className="label">触发词 (用逗号分隔)</label>
        <input
          type="text"
          value={formData.triggers?.join(', ')}
          onChange={(e) => setFormData({ ...formData, triggers: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
          className="input"
          placeholder="搜索, 查找, 查询"
        />
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

// Skill 列表视图
function SkillListView({ skills, onEdit, onDelete, onExecute }: {
  skills: Skill[];
  onEdit: (skill: Skill) => void;
  onDelete: (skill: Skill) => void;
  onExecute: (skill: Skill) => void;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">技能</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">分类</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">版本</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">触发词</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {skills.map((skill) => (
            <tr key={skill.id} className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <Wrench className="w-4 h-4 text-primary-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{skill.display_name}</p>
                    <p className="text-sm text-gray-500">{skill.name}</p>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                  {categoryLabels[skill.category.split('/')[0]] || skill.category}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">{skill.version}</td>
              <td className="px-6 py-4"><StatusBadge status={skill.status} /></td>
              <td className="px-6 py-4">
                <div className="flex flex-wrap gap-1">
                  {skill.triggers.slice(0, 3).map((trigger, i) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                      {trigger}
                    </span>
                  ))}
                  {skill.triggers.length > 3 && (
                    <span className="px-2 py-0.5 text-gray-400 text-xs">+{skill.triggers.length - 3}</span>
                  )}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => onExecute(skill)}
                    className="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="执行"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onEdit(skill)}
                    className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="编辑"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onDelete(skill)}
                    className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="删除"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// 主页面
export function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | 'all'>('all');
  const [view, setView] = useState<'list' | 'form'>('list');
  const [editingSkill, setEditingSkill] = useState<Skill | undefined>();
  const [uniqueCategories, setUniqueCategories] = useState<string[]>([]);
  const [executingSkill, setExecutingSkill] = useState<Skill | null>(null);

  // 从API加载技能
  useEffect(() => {
    const fetchSkills = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await skillsApi.getAll();
        const data = (response as any).data || [];
        setSkills(data);

        // 提取唯一分类
        const cats = [...new Set(data.map((s: Skill) => {
          const cat = s.category.split('/')[0];
          return cat;
        }))].filter(Boolean) as string[];
        setUniqueCategories(cats);
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载技能失败');
        console.error('Failed to fetch skills:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSkills();
  }, []);

  // 过滤技能
  const filteredSkills = skills.filter((skill) => {
    const matchesSearch =
      skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.display_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.description.toLowerCase().includes(searchQuery.toLowerCase());
    // 支持分类路径匹配
    const skillCat = skill.category.split('/')[0];
    const matchesCategory = selectedCategory === 'all' || skillCat === selectedCategory || skill.category.includes(selectedCategory);
    return matchesSearch && matchesCategory;
  });

  // 处理创建
  const handleCreate = () => {
    setEditingSkill(undefined);
    setView('form');
  };

  // 处理编辑
  const handleEdit = (skill: Skill) => {
    setEditingSkill(skill);
    setView('form');
  };

  // 处理删除
  const handleDelete = (skill: Skill) => {
    if (confirm(`确定要删除技能 "${skill.display_name}" 吗？`)) {
      setSkills(skills.filter((s) => s.id !== skill.id));
    }
  };

  // 处理保存
  const handleSave = (skillData: Skill) => {
    if (editingSkill) {
      setSkills(skills.map((s) => (s.id === editingSkill.id ? { ...skillData, id: s.id } : s)));
    } else {
      const newSkill: Skill = {
        ...skillData,
        id: Date.now().toString(),
        created_at: new Date().toISOString().split('T')[0],
        updated_at: new Date().toISOString().split('T')[0],
      };
      setSkills([...skills, newSkill]);
    }
    setView('list');
  };

  // 处理执行
  const handleExecute = (skill: Skill) => {
    setExecutingSkill(skill);
  };

  if (view === 'form') {
    return (
      <div className="page-container">
        <button
          onClick={() => setView('list')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          返回列表
        </button>
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            {editingSkill ? '编辑 Skill' : '创建新 Skill'}
          </h2>
          <SkillForm
            skill={editingSkill}
            onSave={handleSave}
            onCancel={() => setView('list')}
          />
        </div>
      </div>
    );
  }

  // 加载状态
  if (loading) {
    return (
      <div className="page-container animate-fade-in">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          <span className="ml-3 text-gray-600">加载技能列表...</span>
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
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h1 className="page-title">Skills 管理</h1>
          <p className="page-description">管理系统中的所有技能和工具</p>
        </div>
        <button onClick={handleCreate} className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          创建 Skill
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索 skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setSelectedCategory('all')}
            className={cn(
              'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              selectedCategory === 'all'
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            )}
          >
            全部 ({skills.length})
          </button>
          {uniqueCategories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={cn(
                'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                selectedCategory === cat
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              )}
            >
              {categoryLabels[cat] || cat}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="card p-4">
          <p className="text-sm text-gray-500">总 Skills</p>
          <p className="text-2xl font-bold text-gray-900">{skills.length}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">运行中</p>
          <p className="text-2xl font-bold text-green-600">
            {skills.filter((s) => s.status === 'active').length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">已停用</p>
          <p className="text-2xl font-bold text-gray-600">
            {skills.filter((s) => s.status === 'inactive').length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">错误</p>
          <p className="text-2xl font-bold text-red-600">
            {skills.filter((s) => s.status === 'error').length}
          </p>
        </div>
      </div>

      {/* List */}
      <div className="card">
        <SkillListView
          skills={filteredSkills}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onExecute={handleExecute}
        />
      </div>

      {/* 技能执行器 */}
      {executingSkill && (
        <SkillExecutor
          skill={executingSkill}
          onClose={() => setExecutingSkill(null)}
        />
      )}
    </div>
  );
}
