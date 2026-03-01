import { useState, useRef, useEffect, type MouseEvent } from 'react';
import {
  Sparkles,
  Send,
  Bot,
  Loader2,
  Terminal,
  GitBranch,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  Zap,
  History,
  Trash2,
  MessageSquare,
  X,
} from 'lucide-react';
import { cn } from '../utils/cn';
import { intentApi, unifiedApi } from '../services/api';
import type { ExecuteMode, IntentTestResult, LeoExecuteResponse } from '../types';

interface Message {
  id: string;
  type: 'user' | 'system' | 'agent' | 'skill' | 'workflow';
  content: string;
  metadata?: {
    target?: string;
    intent?: string;
    traceId?: string;
    executionTime?: number;
    result?: unknown;
  };
  timestamp: Date;
}

interface ExecutionStep {
  id: string;
  name: string;
  type: 'intent' | 'route' | 'execute' | 'complete';
  status: 'pending' | 'running' | 'success' | 'error';
  description: string;
  result?: unknown;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

const STORAGE_KEY = 'smart_executor_conversations';
const WELCOME_MESSAGE = '你好，我是 Leo AI 智能执行器。输入自然语言后，我会识别意图并通过统一入口执行。';

export function SmartExecutor() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      type: 'system',
      content: WELCOME_MESSAGE,
      timestamp: new Date(),
    },
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [executionSteps, setExecutionSteps] = useState<ExecutionStep[]>([]);
  const [showSteps, setShowSteps] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string>('');
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return;
    try {
      const parsed: Conversation[] = JSON.parse(stored);
      setConversations(parsed);
    } catch {
      // ignore broken cache
    }
  }, []);

  const saveConversations = (next: Conversation[]) => {
    setConversations(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  };

  const createNewConversation = () => {
    const newId = Date.now().toString();
    const conversation: Conversation = {
      id: newId,
      title: '新对话',
      messages: [{ id: 'welcome', type: 'system', content: WELCOME_MESSAGE, timestamp: new Date() }],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    saveConversations([conversation, ...conversations]);
    setCurrentConversationId(newId);
    setMessages(conversation.messages);
    setExecutionSteps([]);
  };

  const loadConversation = (conv: Conversation) => {
    setCurrentConversationId(conv.id);
    setMessages(conv.messages);
    setExecutionSteps([]);
    setShowHistory(false);
  };

  const deleteConversation = (id: string, e: MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    const updated = conversations.filter((c) => c.id !== id);
    saveConversations(updated);
    if (currentConversationId === id) {
      setCurrentConversationId('');
      setMessages([{ id: 'welcome', type: 'system', content: WELCOME_MESSAGE, timestamp: new Date() }]);
    }
  };

  const updateCurrentConversation = (newMessages: Message[]) => {
    if (!currentConversationId) return;
    const updated = conversations.map((conv) => {
      if (conv.id !== currentConversationId) return conv;
      const firstUser = newMessages.find((m) => m.type === 'user');
      const title = firstUser
        ? firstUser.content.slice(0, 20) + (firstUser.content.length > 20 ? '...' : '')
        : conv.title;
      return { ...conv, title, messages: newMessages, updatedAt: Date.now() };
    });
    saveConversations(updated);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, executionSteps]);

  const addStep = (id: string, step: Omit<ExecutionStep, 'id'>) => {
    setExecutionSteps((prev) => [...prev, { ...step, id }]);
  };

  const updateStep = (id: string, updates: Partial<ExecutionStep>) => {
    setExecutionSteps((prev) => prev.map((s) => (s.id === id ? { ...s, ...updates } : s)));
  };

  const inferMessageType = (mode?: ExecuteMode): Message['type'] => {
    if (mode === 'agent') return 'agent';
    if (mode === 'skill') return 'skill';
    if (mode === 'workflow') return 'workflow';
    return 'system';
  };

  const formatResult = (resp: LeoExecuteResponse): string => {
    if (resp.status !== 'ok') return resp.message || '执行失败';
    if (typeof resp.data === 'string') return resp.data;
    if (resp.data && typeof resp.data === 'object') {
      const record = resp.data as Record<string, unknown>;
      if (typeof record.summary === 'string' && record.summary.trim()) return record.summary;
      if (typeof record.response === 'string') return record.response;
      if (typeof record.message === 'string') return record.message;
      if (typeof record.task === 'string') return `已完成任务：${record.task}`;
      return JSON.stringify(resp.data, null, 2);
    }
    return resp.message || '执行完成';
  };

  const getErrorMessage = (error: unknown): string => {
    if (error instanceof Error) return error.message;
    if (typeof error === 'string' && error.trim()) return error;
    if (error && typeof error === 'object' && 'message' in error) {
      const msg = (error as { message?: unknown }).message;
      if (typeof msg === 'string' && msg.trim()) return msg;
    }
    return '未知错误';
  };

  const persistMessages = (updatedMessages: Message[]) => {
    if (!currentConversationId) {
      const newId = Date.now().toString();
      const firstUser = updatedMessages.find((m) => m.type === 'user');
      const title = firstUser
        ? firstUser.content.slice(0, 20) + (firstUser.content.length > 20 ? '...' : '')
        : '新对话';
      const newConv: Conversation = {
        id: newId,
        title,
        messages: updatedMessages,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      setCurrentConversationId(newId);
      saveConversations([newConv, ...conversations]);
    } else {
      updateCurrentConversation(updatedMessages);
    }
  };

  const handleExecute = async () => {
    if (!input.trim() || isProcessing) return;

    const userMessage = input.trim();
    setInput('');
    setIsProcessing(true);
    setExecutionSteps([]);

    const userMsg: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const step1Id = 'step-intent';
      addStep(step1Id, { name: '意图识别', type: 'intent', status: 'running', description: '解析输入语义...' });

      const intentResult = await intentApi.test(userMessage);
      const intentData: IntentTestResult | undefined = intentResult.data;
      if (!intentData) {
        throw new Error('意图识别结果为空');
      }

      const mode = (intentData.match.intent_type as ExecuteMode) || 'auto';
      const target = intentData.match.target;
      const params = intentData.match.params || {};

      updateStep(step1Id, {
        status: 'success',
        description: `识别为 ${mode}（置信度 ${(intentData.match.confidence * 100).toFixed(0)}%）`,
        result: intentData.match,
      });

      const step2Id = 'step-route';
      addStep(step2Id, {
        name: '路由决策',
        type: 'route',
        status: 'running',
        description: target ? `目标：${target}` : '自动路由',
      });
      updateStep(step2Id, {
        status: 'success',
        description: target ? `已路由到 ${target}` : '将由后端自动决策',
        result: intentData.routing,
      });

      const step3Id = 'step-exec';
      addStep(step3Id, {
        name: '统一执行',
        type: 'execute',
        status: 'running',
        description: '调用 /api/v2/execute ...',
      });

      const execResult = await unifiedApi.execute({
        intent: userMessage,
        mode: target ? mode : 'auto',
        target,
        method: mode === 'skill' ? 'execute' : undefined,
        params,
      });

      updateStep(step3Id, {
        status: execResult.status === 'ok' ? 'success' : 'error',
        description: execResult.message || '执行完成',
        result: execResult,
      });

      addStep('step-complete', { name: '完成', type: 'complete', status: 'success', description: '流程结束' });

      const systemMsg: Message = {
        id: `${Date.now()}-assistant`,
        type: inferMessageType(execResult.intent as ExecuteMode),
        content: formatResult(execResult),
        metadata: {
          target: execResult.target,
          intent: execResult.intent,
          traceId: execResult.trace_id,
          executionTime: intentData.execution_time_ms,
          result: execResult,
        },
        timestamp: new Date(),
      };

      setMessages((prev) => {
        const updated = [...prev, systemMsg];
        persistMessages(updated);
        return updated;
      });
    } catch (error) {
      const errorText = getErrorMessage(error);
      setExecutionSteps((prev) =>
        prev.map((s) => (s.status === 'running' ? { ...s, status: 'error', description: `${s.description}（已中断）` } : s))
      );
      addStep('step-failed', { name: '执行失败', type: 'complete', status: 'error', description: '请检查服务日志' });
      const errorMsg: Message = {
        id: `${Date.now()}-error`,
        type: 'system',
        content: `执行失败：${errorText}`,
        timestamp: new Date(),
      };
      setMessages((prev) => {
        const updated = [...prev, errorMsg];
        persistMessages(updated);
        return updated;
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const getMessageIcon = (type: Message['type']) => {
    switch (type) {
      case 'user':
        return <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-sm font-medium">我</div>;
      case 'agent':
        return <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center"><Bot className="w-4 h-4 text-white" /></div>;
      case 'skill':
        return <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center"><Terminal className="w-4 h-4 text-white" /></div>;
      case 'workflow':
        return <div className="w-8 h-8 rounded-full bg-amber-500 flex items-center justify-center"><GitBranch className="w-4 h-4 text-white" /></div>;
      default:
        return <div className="w-8 h-8 rounded-full bg-gray-500 flex items-center justify-center"><Sparkles className="w-4 h-4 text-white" /></div>;
    }
  };

  const getStepIcon = (status: ExecutionStep['status']) => {
    if (status === 'running') return <Loader2 className="w-4 h-4 animate-spin text-primary-500" />;
    if (status === 'success') return <CheckCircle2 className="w-4 h-4 text-green-500" />;
    if (status === 'error') return <div className="w-4 h-4 rounded-full bg-red-500" />;
    return <div className="w-4 h-4 rounded-full bg-gray-300" />;
  };

  return (
    <div className="page-container animate-fade-in h-[calc(100vh-4rem)] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary-600" />
            统一智能执行器
          </h1>
          <p className="page-description">一个输入框，统一调度 Skill / Agent / Workflow</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setShowHistory(true)} className="btn-secondary flex items-center gap-2">
            <History className="w-4 h-4" />
            历史对话 ({conversations.length})
          </button>
          <button onClick={createNewConversation} className="btn-secondary flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            新对话
          </button>
        </div>
      </div>

      {executionSteps.length > 0 && (
        <div className="card mb-4 overflow-hidden">
          <button
            onClick={() => setShowSteps(!showSteps)}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-500" />
              <span className="font-medium text-gray-700">执行轨迹</span>
              <span className="text-xs text-gray-400">({executionSteps.length} 步)</span>
            </div>
            {showSteps ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
          </button>
          {showSteps && (
            <div className="px-4 pb-4 space-y-2">
              {executionSteps.map((step, index) => (
                <div key={step.id} className="flex items-start gap-3">
                  <div className="flex flex-col items-center">
                    {getStepIcon(step.status)}
                    {index < executionSteps.length - 1 && <div className="w-0.5 h-6 bg-gray-200 mt-1" />}
                  </div>
                  <div className="flex-1 pb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-700">{step.name}</span>
                      <span className={cn(
                        'text-xs px-2 py-0.5 rounded-full',
                        step.status === 'running' && 'bg-blue-100 text-blue-600',
                        step.status === 'success' && 'bg-green-100 text-green-600',
                        step.status === 'error' && 'bg-red-100 text-red-600',
                        step.status === 'pending' && 'bg-gray-100 text-gray-600'
                      )}>
                        {step.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-0.5">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="flex-1 overflow-auto card p-4 mb-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={cn('flex gap-3', message.type === 'user' ? 'flex-row-reverse' : 'flex-row')}>
              {getMessageIcon(message.type)}
              <div className={cn(
                'max-w-[80%] rounded-xl p-3',
                message.type === 'user' ? 'bg-primary-500 text-white' : 'bg-gray-50 border border-gray-100'
              )}>
                <div className={cn('text-sm whitespace-pre-wrap leading-relaxed', message.type === 'user' ? 'text-white' : 'text-gray-700')}>
                  {message.content}
                </div>
                {message.metadata?.traceId && (
                  <p className="text-xs text-gray-400 mt-2">trace_id: {message.metadata.traceId}</p>
                )}
                {Boolean(message.metadata?.result) && message.type !== 'user' && (
                  <details className="mt-2">
                    <summary className="text-xs text-gray-500 cursor-pointer">查看技术详情</summary>
                    <pre className="mt-2 p-2 bg-white rounded text-xs text-gray-600 overflow-auto max-h-40">
                      {JSON.stringify(message.metadata?.result, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          ))}

          {isProcessing && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-500 flex items-center justify-center">
                <Loader2 className="w-4 h-4 text-white animate-spin" />
              </div>
              <div className="bg-gray-50 border border-gray-100 rounded-xl p-3 text-sm text-gray-500">执行中...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="card p-4">
        <div className="flex items-center gap-3">
          <Lightbulb className="w-5 h-5 text-amber-500 shrink-0" />
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleExecute()}
            placeholder="输入你的任务，例如：帮我分析宁波商业地产本周动态"
            className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            disabled={isProcessing}
          />
          <button onClick={handleExecute} disabled={!input.trim() || isProcessing} className="btn-primary flex items-center gap-2 px-6">
            {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            发送
          </button>
        </div>
      </div>

      {showHistory && (
        <div className="fixed inset-0 z-50 flex">
          <div className="flex-1 bg-black/30" onClick={() => setShowHistory(false)} />
          <div className="w-80 bg-white shadow-xl flex flex-col">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                <History className="w-5 h-5" />
                历史对话
              </h3>
              <button onClick={() => setShowHistory(false)} className="p-1 hover:bg-gray-100 rounded">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-2">
              {conversations.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>暂无历史对话</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {conversations.map((conv) => (
                    <div
                      key={conv.id}
                      onClick={() => loadConversation(conv)}
                      className={cn(
                        'p-3 rounded-lg cursor-pointer group relative',
                        currentConversationId === conv.id
                          ? 'bg-primary-50 border border-primary-200'
                          : 'hover:bg-gray-50 border border-transparent'
                      )}
                    >
                      <div className="flex items-start gap-2">
                        <MessageSquare className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm text-gray-800 truncate">{conv.title}</p>
                          <p className="text-xs text-gray-400 mt-1">
                            {new Date(conv.updatedAt).toLocaleString('zh-CN', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={(e) => deleteConversation(conv.id, e)}
                        className="absolute top-2 right-2 p-1 opacity-0 group-hover:opacity-100 hover:bg-red-50 rounded transition-opacity"
                      >
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
