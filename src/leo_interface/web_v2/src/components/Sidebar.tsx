import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Wrench,
  Users,
  Workflow,
  Brain,
  Search,
  Database,
  Settings,
  Zap,
  Sparkles,
} from 'lucide-react';
import { cn } from '../utils/cn';

const navItems = [
  { id: 'dashboard', label: '仪表盘', icon: LayoutDashboard, path: '/' },
  { id: 'smart', label: '智能执行', icon: Sparkles, path: '/smart' },
  { id: 'skills', label: 'Skills', icon: Wrench, path: '/skills' },
  { id: 'agents', label: 'Agents', icon: Users, path: '/agents' },
  { id: 'workflows', label: 'Workflows', icon: Workflow, path: '/workflows' },
  { id: 'memory', label: '共享记忆', icon: Database, path: '/memory' },
  { id: 'intent', label: '意图调试', icon: Search, path: '/intent' },
  { id: 'evolution', label: '技能进化', icon: Zap, path: '/evolution' },
  { id: 'settings', label: '设置', icon: Settings, path: '/settings' },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg text-gray-900">Leo AI</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <NavLink
              key={item.id}
              to={item.path}
              className={cn(
                'sidebar-item',
                isActive && 'active'
              )}
            >
              <Icon className={cn(
                'w-5 h-5',
                isActive ? 'text-primary-600' : 'text-gray-400'
              )} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3 px-4 py-2 text-sm text-gray-500">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span>系统运行正常</span>
        </div>
        <div className="px-4 py-1 text-xs text-gray-400">
          v1.0.0
        </div>
      </div>
    </aside>
  );
}
