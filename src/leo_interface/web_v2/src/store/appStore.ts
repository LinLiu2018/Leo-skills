import { create } from 'zustand';
import type { SystemStats, CategoryStats } from '../types';
import { systemApi } from '../services/api';

interface AppState {
  stats: SystemStats | null;
  categoryStats: CategoryStats[];
  isLoading: boolean;
  error: string | null;
  setStats: (stats: SystemStats) => void;
  setCategoryStats: (stats: CategoryStats[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  refreshStats: () => Promise<void>;
}

export const useAppStore = create<AppState>((set) => ({
  stats: null,
  categoryStats: [],
  isLoading: false,
  error: null,

  setStats: (stats) => set({ stats }),
  setCategoryStats: (categoryStats) => set({ categoryStats }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  refreshStats: async () => {
    set({ isLoading: true, error: null });
    try {
      const [statsResponse, categoryResponse] = await Promise.all([
        systemApi.getStats(),
        systemApi.getCategoryStats(),
      ]);

      const statsPayload = statsResponse.data;
      const categoryPayload = categoryResponse.data;

      set({
        stats: statsPayload || {
          total_skills: 0,
          total_agents: 0,
          total_workflows: 0,
          active_tasks: 0,
          memory_entries: 0,
          uptime_hours: 0,
        },
        categoryStats: categoryPayload || [],
      });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : '获取统计数据失败' });
    } finally {
      set({ isLoading: false });
    }
  },
}));
