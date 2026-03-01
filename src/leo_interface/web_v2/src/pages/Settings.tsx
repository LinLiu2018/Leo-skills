import { useState } from 'react';
import {
  Settings as SettingsIcon,
  Server,
  Shield,
  Bell,
  Database,
  Globe,
  Key,
  Save,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '../utils/cn';

interface SettingSection {
  id: string;
  title: string;
  icon: React.ElementType;
  description: string;
}

const sections: SettingSection[] = [
  { id: 'general', title: '通用设置', icon: SettingsIcon, description: '系统基本配置' },
  { id: 'api', title: 'API 配置', icon: Key, description: 'API密钥和端点设置' },
  { id: 'notifications', title: '通知设置', icon: Bell, description: '消息和提醒配置' },
  { id: 'database', title: '数据库', icon: Database, description: '数据存储配置' },
  { id: 'security', title: '安全', icon: Shield, description: '访问控制和安全设置' },
  { id: 'system', title: '系统', icon: Server, description: '系统维护和日志' },
];

function GeneralSettings() {
  const [settings, setSettings] = useState({
    language: 'zh-CN',
    timezone: 'Asia/Shanghai',
    auto_update: true,
    debug_mode: false,
  });

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="label">系统语言</label>
          <select
            value={settings.language}
            onChange={(e) => setSettings({ ...settings, language: e.target.value })}
            className="input"
          >
            <option value="zh-CN">简体中文</option>
            <option value="en-US">English</option>
          </select>
        </div>
        <div>
          <label className="label">时区</label>
          <select
            value={settings.timezone}
            onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
            className="input"
          >
            <option value="Asia/Shanghai">Asia/Shanghai (UTC+8)</option>
            <option value="UTC">UTC</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={settings.auto_update}
            onChange={(e) => setSettings({ ...settings, auto_update: e.target.checked })}
            className="w-4 h-4 text-primary-600 rounded"
          />
          <span className="text-gray-700">自动更新能力索引</span>
        </label>
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={settings.debug_mode}
            onChange={(e) => setSettings({ ...settings, debug_mode: e.target.checked })}
            className="w-4 h-4 text-primary-600 rounded"
          />
          <span className="text-gray-700">调试模式</span>
        </label>
      </div>
    </div>
  );
}

function ApiSettings() {
  const [apiKeys, setApiKeys] = useState({
    openai: 'sk-****',
    anthropic: 'sk-****',
    feishu: 'cli_****',
  });

  return (
    <div className="space-y-6">
      <div>
        <label className="label">OpenAI API Key</label>
        <div className="flex gap-2">
          <input
            type="password"
            value={apiKeys.openai}
            onChange={(e) => setApiKeys({ ...apiKeys, openai: e.target.value })}
            className="input flex-1"
          />
          <button className="btn-secondary">更新</button>
        </div>
      </div>

      <div>
        <label className="label">Anthropic API Key</label>
        <div className="flex gap-2">
          <input
            type="password"
            value={apiKeys.anthropic}
            onChange={(e) => setApiKeys({ ...apiKeys, anthropic: e.target.value })}
            className="input flex-1"
          />
          <button className="btn-secondary">更新</button>
        </div>
      </div>

      <div>
        <label className="label">飞书 App ID</label>
        <div className="flex gap-2">
          <input
            type="password"
            value={apiKeys.feishu}
            onChange={(e) => setApiKeys({ ...apiKeys, feishu: e.target.value })}
            className="input flex-1"
          />
          <button className="btn-secondary">更新</button>
        </div>
      </div>
    </div>
  );
}

function DatabaseSettings() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="label">数据库类型</label>
          <select className="input">
            <option value="sqlite">SQLite (默认)</option>
            <option value="postgresql">PostgreSQL</option>
          </select>
        </div>
        <div>
          <label className="label">自动备份</label>
          <select className="input">
            <option value="daily">每天</option>
            <option value="weekly">每周</option>
            <option value="never">从不</option>
          </select>
        </div>
      </div>

      <div className="p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">数据库状态</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">连接状态</span>
            <span className="text-green-600 flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4" />
              正常
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">数据大小</span>
            <span className="text-gray-900">45.2 MB</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">上次备份</span>
            <span className="text-gray-900">2024-02-04 03:00:00</span>
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <button className="btn-secondary">
          <RefreshCw className="w-4 h-4 mr-2" />
          立即备份
        </button>
        <button className="btn-primary">
          导出数据
        </button>
      </div>
    </div>
  );
}

function SystemSettings() {
  return (
    <div className="space-y-6">
      <div className="p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-4">系统信息</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">版本</span>
            <p className="text-gray-900">v1.0.0</p>
          </div>
          <div>
            <span className="text-gray-500">运行时间</span>
            <p className="text-gray-900">168 小时</p>
          </div>
          <div>
            <span className="text-gray-500">Python 版本</span>
            <p className="text-gray-900">3.11.0</p>
          </div>
          <div>
            <span className="text-gray-500">内存使用</span>
            <p className="text-gray-900">245 MB / 2 GB</p>
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <button className="btn-secondary">
          <RefreshCw className="w-4 h-4 mr-2" />
          重启系统
        </button>
        <button className="btn-primary">
          查看日志
        </button>
      </div>
    </div>
  );
}

export function Settings() {
  const [activeSection, setActiveSection] = useState('general');

  const renderSection = () => {
    switch (activeSection) {
      case 'general':
        return <GeneralSettings />;
      case 'api':
        return <ApiSettings />;
      case 'database':
        return <DatabaseSettings />;
      case 'system':
        return <SystemSettings />;
      default:
        return (
          <div className="text-center text-gray-500 py-12">
            <SettingsIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>该设置页面开发中</p>
          </div>
        );
    }
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">设置</h1>
        <p className="page-description">配置系统参数和集成选项</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-64 space-y-1">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={cn(
                  'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors',
                  activeSection === section.id
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                )}
              >
                <Icon className="w-5 h-5" />
                <div>
                  <p className="font-medium">{section.title}</p>
                  <p className="text-xs opacity-70">{section.description}</p>
                </div>
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">
                {sections.find(s => s.id === activeSection)?.title}
              </h2>
              <button className="btn-primary">
                <Save className="w-4 h-4 mr-2" />
                保存更改
              </button>
            </div>
            {renderSection()}
          </div>
        </div>
      </div>
    </div>
  );
}
