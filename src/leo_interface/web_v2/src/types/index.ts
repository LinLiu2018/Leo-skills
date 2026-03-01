export interface Skill {
  id: string;
  name: string;
  display_name: string;
  version: string;
  category: SkillCategory;
  description: string;
  author: string;
  status: 'active' | 'inactive' | 'error';
  triggers: string[];
  inputs: SkillInput[];
  outputs: SkillOutput[];
  created_at: string;
  updated_at: string;
}

export type SkillCategory = string;

export interface SkillInput {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  description?: string;
  default?: unknown;
}

export interface SkillOutput {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  description?: string;
}

export interface Agent {
  id: string;
  name: string;
  display_name: string;
  description: string;
  role: string;
  capabilities: string[];
  skills: string[];
  status: 'active' | 'inactive' | 'error';
  created_at: string;
  updated_at: string;
}

export interface Workflow {
  id: string;
  name: string;
  display_name: string;
  version: string;
  description: string;
  status: 'active' | 'inactive' | 'error';
  steps: WorkflowStep[];
  inputs: WorkflowInput[];
  created_at: string;
  updated_at: string;
}

export interface WorkflowStep {
  name: string;
  type: 'sequential' | 'parallel' | 'conditional';
  agent?: string;
  skill?: string;
  retries?: number;
  timeout?: number;
  parallel_steps?: WorkflowStep[];
  condition?: string;
  on_true?: string;
  on_false?: string;
}

export interface WorkflowInput {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  description?: string;
}

export interface MemoryEntry {
  id: string;
  key: string;
  value: string;
  category: string;
  importance: number;
  created_at: string;
  updated_at: string;
  expires_at?: string;
}

export interface MemoryStats {
  total_entries: number;
  categories: Record<string, number>;
  by_importance: Record<number, number>;
}

export interface IntentMatch {
  intent_type: 'agent' | 'skill' | 'workflow' | 'query';
  target: string;
  confidence: number;
  params: Record<string, unknown>;
  alternatives: IntentAlternative[];
}

export interface IntentAlternative {
  target: string;
  confidence: number;
}

export interface IntentTestResult {
  input: string;
  match: IntentMatch;
  routing: RoutingDecision;
  execution_time_ms: number;
}

export interface RoutingDecision {
  action: string;
  target: string;
  params: Record<string, unknown>;
}

export interface SystemStats {
  total_skills: number;
  total_agents: number;
  total_workflows: number;
  active_tasks: number;
  memory_entries: number;
  uptime_hours: number;
}

export interface CategoryStats {
  category: string;
  count: number;
  label: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: number;
}

export type ExecuteMode = 'auto' | 'skill' | 'agent' | 'workflow';

export interface LeoExecuteRequest {
  intent: string;
  mode?: ExecuteMode;
  target?: string;
  method?: string;
  params?: Record<string, unknown>;
  trace_id?: string;
}

export interface LeoExecuteResponse {
  trace_id: string;
  status: 'ok' | 'error';
  intent?: string;
  target?: string;
  data?: unknown;
  error_code?: string;
  message: string;
}
