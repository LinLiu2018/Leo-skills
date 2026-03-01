import axios from 'axios';
import type {
  ApiResponse,
  Skill,
  Agent,
  Workflow,
  MemoryEntry,
  MemoryStats,
  IntentMatch,
  IntentTestResult,
  SystemStats,
  CategoryStats,
  LeoExecuteRequest,
  LeoExecuteResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

api.interceptors.request.use(
  (config) => {
    const token = import.meta.env.VITE_WEB_API_TOKEN as string | undefined;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      return Promise.reject(error.response.data?.error || '请求失败');
    }
    return Promise.reject('网络错误');
  }
);

export interface SkillMethod {
  name: string;
  doc: string;
  params: {
    name: string;
    required: boolean;
    default: string | null;
    type: string;
  }[];
}

export interface SkillExecuteResult {
  result: unknown;
  skill_id: string;
  method: string;
}

export interface AgentExecuteResult {
  response: string;
  agent: string;
  task: string;
  execution_time_ms: number;
  agent_name?: string;
}

export const skillsApi = {
  getAll: () => api.get<ApiResponse<Skill[]>>('/skills'),
  getById: (id: string) => api.get<ApiResponse<Skill>>(`/skills/${id}`),
  create: (data: Omit<Skill, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<ApiResponse<Skill>>('/skills', data),
  update: (id: string, data: Partial<Skill>) =>
    api.put<ApiResponse<Skill>>(`/skills/${id}`, data),
  delete: (id: string) => api.delete<ApiResponse<void>>(`/skills/${id}`),
  getMethods: (id: string) =>
    api.get<ApiResponse<SkillMethod[]>>(`/skills/${id}/methods`),
  execute: (id: string, method: string, params: Record<string, unknown>) =>
    api.post<ApiResponse<SkillExecuteResult>>(`/skills/${id}/execute`, { method, params }),
  getByCategory: (category: string) =>
    api.get<ApiResponse<Skill[]>>(`/skills?category=${category}`),
};

export const agentsApi = {
  getAll: () => api.get<ApiResponse<Agent[]>>('/agents'),
  getById: (id: string) => api.get<ApiResponse<Agent>>(`/agents/${id}`),
  create: (data: Omit<Agent, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<ApiResponse<Agent>>('/agents', data),
  update: (id: string, data: Partial<Agent>) =>
    api.put<ApiResponse<Agent>>(`/agents/${id}`, data),
  delete: (id: string) => api.delete<ApiResponse<void>>(`/agents/${id}`),
  getCapabilities: (id: string) =>
    api.get<ApiResponse<string[]>>(`/agents/${id}/capabilities`),
  execute: (id: string, message: string) =>
    api.post<ApiResponse<AgentExecuteResult>>(`/agents/${id}/execute`, { message }),
};

export const workflowsApi = {
  getAll: () => api.get<ApiResponse<Workflow[]>>('/workflows') as unknown as Promise<ApiResponse<Workflow[]>>,
  getById: (id: string) => api.get<ApiResponse<Workflow>>(`/workflows/${id}`),
  create: (data: Omit<Workflow, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<ApiResponse<Workflow>>('/workflows', data),
  update: (id: string, data: Partial<Workflow>) =>
    api.put<ApiResponse<Workflow>>(`/workflows/${id}`, data),
  delete: (id: string) => api.delete<ApiResponse<void>>(`/workflows/${id}`),
  execute: (id: string, inputs: Record<string, unknown>) =>
    api.post<ApiResponse<unknown>>(`/workflows/${id}/execute`, { inputs }) as unknown as Promise<ApiResponse<unknown>>,
  validate: (yaml: string) =>
    api.post<ApiResponse<{ valid: boolean; errors?: string[] }>>('/workflows/validate', { yaml }),
};

export const memoryApi = {
  getAll: (category?: string) =>
    api.get<ApiResponse<MemoryEntry[]>>(category ? `/memory?category=${category}` : '/memory'),
  getByKey: (key: string) => api.get<ApiResponse<MemoryEntry>>(`/memory/${key}`),
  create: (data: Omit<MemoryEntry, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<ApiResponse<MemoryEntry>>('/memory', data),
  update: (key: string, data: Partial<MemoryEntry>) =>
    api.put<ApiResponse<MemoryEntry>>(`/memory/${key}`, data),
  delete: (key: string) => api.delete<ApiResponse<void>>(`/memory/${key}`),
  search: (query: string) =>
    api.get<ApiResponse<MemoryEntry[]>>(`/memory/search?q=${encodeURIComponent(query)}`),
  getStats: () => api.get<ApiResponse<MemoryStats>>('/memory/stats'),
  cleanup: () => api.post<ApiResponse<{ removed: number }>>('/memory/cleanup'),
};

export const intentApi = {
  recognize: (text: string) =>
    api.post<ApiResponse<IntentMatch>>('/intent/recognize', { text }),
  route: (text: string) =>
    api.post<ApiResponse<{ action: string; target: string; params: Record<string, unknown> }>>('/intent/route', { text }),
  test: (text: string) =>
    api.post<ApiResponse<IntentTestResult>>('/intent/test', { text }) as unknown as Promise<ApiResponse<IntentTestResult>>,
  batchTest: (texts: string[]) =>
    api.post<ApiResponse<IntentTestResult[]>>('/intent/batch-test', { texts }),
};

export const systemApi = {
  getStats: () => api.get<ApiResponse<SystemStats>>('/system/stats') as unknown as Promise<ApiResponse<SystemStats>>,
  getCategoryStats: () => api.get<ApiResponse<CategoryStats[]>>('/system/category-stats') as unknown as Promise<ApiResponse<CategoryStats[]>>,
  getHealth: () => api.get<ApiResponse<{ status: string; uptime: number }>>('/system/health'),
  reload: () => api.post<ApiResponse<void>>('/system/reload'),
};

export const unifiedApi = {
  execute: (payload: LeoExecuteRequest) =>
    api.post<LeoExecuteResponse>('/v2/execute', payload) as unknown as Promise<LeoExecuteResponse>,
};

export default api;
