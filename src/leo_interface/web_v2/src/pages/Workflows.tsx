import { useEffect, useState } from 'react';
import { GitBranch, Play, RefreshCw } from 'lucide-react';
import type { Workflow } from '../types';
import { workflowsApi } from '../services/api';

export function Workflows() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [result, setResult] = useState<string>('');

  const load = async () => {
    setLoading(true);
    try {
      const response = await workflowsApi.getAll();
      setWorkflows(response.data || []);
    } catch (error) {
      setResult(`加载失败: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setLoading(false);
    }
  };

  const runWorkflow = async (workflowId: string) => {
    setRunningId(workflowId);
    try {
      const response = await workflowsApi.execute(workflowId, { topic: 'demo' });
      setResult(JSON.stringify(response.data, null, 2));
    } catch (error) {
      setResult(`执行失败: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setRunningId(null);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="page-container animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <GitBranch className="w-6 h-6 text-primary-600" />
            Workflows
          </h1>
          <p className="page-description">查看并执行工作流</p>
        </div>
        <button onClick={load} className="btn-secondary flex items-center gap-2" disabled={loading}>
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          刷新
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {workflows.map((workflow) => (
          <div key={workflow.id} className="card p-4">
            <h3 className="font-semibold text-gray-800">{workflow.display_name || workflow.name}</h3>
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">{workflow.description || '无描述'}</p>
            <div className="mt-3 text-xs text-gray-400">步骤: {workflow.steps?.length || 0}</div>
            <button
              className="btn-primary mt-4 flex items-center gap-2"
              onClick={() => runWorkflow(workflow.id)}
              disabled={runningId === workflow.id}
            >
              <Play className={`w-4 h-4 ${runningId === workflow.id ? 'animate-pulse' : ''}`} />
              {runningId === workflow.id ? '执行中...' : '执行'}
            </button>
          </div>
        ))}
      </div>

      <div className="card p-4 mt-6">
        <h3 className="font-semibold text-gray-800 mb-2">执行结果</h3>
        <pre className="bg-gray-50 p-3 rounded text-xs text-gray-700 overflow-auto max-h-80 whitespace-pre-wrap">
          {result || '暂无执行结果'}
        </pre>
      </div>
    </div>
  );
}
