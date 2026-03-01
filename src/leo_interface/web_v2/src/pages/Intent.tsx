import { useState } from 'react';
import {
  Search,
  Brain,
  Send,
  ChevronRight,
  Bot,
  Wrench,
  Workflow,
  MessageSquare,
  Sparkles,
  Zap,
  History,
  Trash2,
} from 'lucide-react';
import type { IntentMatch, IntentTestResult } from '../types';
import { cn } from '../utils/cn';

// 模拟测试结果
const mockTestHistory: IntentTestResult[] = [
  {
    input: '帮我研究量子计算',
    match: {
      intent_type: 'agent',
      target: 'research_agent',
      confidence: 0.92,
      params: { topic: '量子计算' },
      alternatives: [],
    },
    routing: {
      action: 'delegate_to_agent',
      target: 'research_agent',
      params: { query: '量子计算' },
    },
    execution_time_ms: 45,
  },
  {
    input: '搜索最新的AI新闻',
    match: {
      intent_type: 'skill',
      target: 'web_search_skill',
      confidence: 0.88,
      params: { query: 'AI新闻' },
      alternatives: [],
    },
    routing: {
      action: 'execute_skill',
      target: 'web_search_skill',
      params: { query: '最新的AI新闻' },
    },
    execution_time_ms: 32,
  },
  {
    input: '运行内容生产流水线',
    match: {
      intent_type: 'workflow',
      target: 'content_pipeline',
      confidence: 0.95,
      params: {},
      alternatives: [],
    },
    routing: {
      action: 'execute_workflow',
      target: 'content_pipeline',
      params: {},
    },
    execution_time_ms: 28,
  },
];

// 类型图标
function TypeIcon({ type }: { type: IntentMatch['intent_type'] }) {
  const config = {
    agent: { icon: Bot, color: 'bg-blue-500', label: 'Agent' },
    skill: { icon: Wrench, color: 'bg-green-500', label: 'Skill' },
    workflow: { icon: Workflow, color: 'bg-purple-500', label: 'Workflow' },
    query: { icon: MessageSquare, color: 'bg-gray-500', label: 'Query' },
  };
  const { icon: Icon, color, label } = config[type];

  return (
    <div className={cn('inline-flex items-center gap-2 px-3 py-1 rounded-full text-white text-sm', color)}>
      <Icon className="w-4 h-4" />
      <span>{label}</span>
    </div>
  );
}

// 置信度条
function ConfidenceBar({ value }: { value: number }) {
  const getColor = (v: number) => {
    if (v >= 0.9) return 'bg-green-500';
    if (v >= 0.7) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-500', getColor(value))}
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="text-sm font-medium text-gray-700">{(value * 100).toFixed(1)}%</span>
    </div>
  );
}

// 测试结果卡片
function ResultCard({ result }: { result: IntentTestResult }) {
  return (
    <div className="card p-6 animate-fade-in">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm text-gray-500 mb-1">输入</p>
          <p className="text-lg font-medium text-gray-900">"{result.input}"</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-400">执行时间</p>
          <p className="text-sm font-medium">{result.execution_time_ms}ms</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-4">
        <div>
          <p className="text-sm text-gray-500 mb-2">识别的意图</p>
          <TypeIcon type={result.match.intent_type} />
          <p className="mt-2 text-sm font-medium text-gray-900">{result.match.target}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500 mb-2">置信度</p>
          <ConfidenceBar value={result.match.confidence} />
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-sm text-gray-500 mb-2">路由决策</p>
        <div className="flex items-center gap-2 text-sm">
          <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded font-medium">
            {result.routing.action}
          </span>
          <ChevronRight className="w-4 h-4 text-gray-400" />
          <span className="font-medium text-gray-900">{result.routing.target}</span>
        </div>
        {Object.keys(result.routing.params).length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-1">提取的参数</p>
            <pre className="text-xs text-gray-700 bg-white p-2 rounded border overflow-x-auto">
              {JSON.stringify(result.routing.params, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

// 主页面
export function Intent() {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<IntentTestResult[]>(mockTestHistory);
  const [currentResult, setCurrentResult] = useState<IntentTestResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleTest = async () => {
    if (!input.trim()) return;

    setIsLoading(true);

    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 500));

    // 模拟结果
    const mockResult: IntentTestResult = {
      input: input.trim(),
      match: {
        intent_type: Math.random() > 0.5 ? 'agent' : 'skill',
        target: Math.random() > 0.5 ? 'research_agent' : 'web_search_skill',
        confidence: 0.7 + Math.random() * 0.25,
        params: { query: input.trim() },
        alternatives: [],
      },
      routing: {
        action: 'delegate_to_agent',
        target: 'research_agent',
        params: { query: input.trim() },
      },
      execution_time_ms: Math.floor(20 + Math.random() * 50),
    };

    setCurrentResult(mockResult);
    setHistory([mockResult, ...history]);
    setIsLoading(false);
  };

  const clearHistory = () => {
    if (confirm('确定要清空测试历史吗？')) {
      setHistory([]);
      setCurrentResult(null);
    }
  };

  return (
    <div className="page-container animate-fade-in">
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">意图识别调试</h1>
        <p className="page-description">
          测试和优化意图识别引擎，查看输入如何被解析和路由
        </p>
      </div>

      {/* Test Input */}
      <div className="card p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-primary-100 rounded-lg">
            <Brain className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">测试输入</h3>
            <p className="text-sm text-gray-500">输入自然语言，查看识别结果</p>
          </div>
        </div>

        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleTest()}
            placeholder="例如：帮我研究量子计算、搜索AI新闻..."
            className="flex-1 input"
          />
          <button
            onClick={handleTest}
            disabled={!input.trim() || isLoading}
            className={cn(
              'btn-primary min-w-[100px]',
              (!input.trim() || isLoading) && 'opacity-50 cursor-not-allowed'
            )}
          >
            {isLoading ? (
              <Zap className="w-4 h-4 animate-pulse" />
            ) : (
              <Send className="w-4 h-4 mr-2" />
            )}
            测试
          </button>
        </div>

        {/* Quick Examples */}
        <div className="mt-4 flex flex-wrap gap-2">
          <span className="text-sm text-gray-500">快速示例：</span>
          {['研究区块链技术', '分析销售数据', '生成周报', '剪辑视频'].map((example) => (
            <button
              key={example}
              onClick={() => setInput(example)}
              className="text-sm text-primary-600 hover:text-primary-700 hover:underline"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Current Result */}
      {currentResult && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-yellow-500" />
            当前结果
          </h3>
          <ResultCard result={currentResult} />
        </div>
      )}

      {/* History */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <History className="w-5 h-5 text-gray-500" />
            测试历史
          </h3>
          {history.length > 0 && (
            <button
              onClick={clearHistory}
              className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1"
            >
              <Trash2 className="w-4 h-4" />
              清空历史
            </button>
          )}
        </div>

        <div className="space-y-4">
          {history.slice(0, 5).map((result, index) => (
            <div
              key={index}
              onClick={() => setCurrentResult(result)}
              className="card p-4 cursor-pointer hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <TypeIcon type={result.match.intent_type} />
                  <span className="font-medium text-gray-900">"{result.input}"</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-500">{result.match.target}</span>
                  <span className={cn(
                    'text-sm font-medium',
                    result.match.confidence >= 0.9 ? 'text-green-600' :
                    result.match.confidence >= 0.7 ? 'text-yellow-600' : 'text-red-600'
                  )}>
                    {(result.match.confidence * 100).toFixed(0)}%
                  </span>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </div>
              </div>
            </div>
          ))}

          {history.length === 0 && (
            <div className="card p-12 text-center text-gray-500">
              <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>暂无测试记录</p>
              <p className="text-sm">在上方输入内容开始测试</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
