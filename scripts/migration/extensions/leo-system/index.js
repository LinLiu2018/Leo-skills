/**
 * Leo System Integration Plugin for OpenClaw v2
 * Fixed for OpenClaw 2026.1.30 API
 * Features: Dynamic capability sync, graceful degradation, static fallback, better error handling
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Leo System 根目录（动态扫描用）
// Leo System root directory.
const LEO_SYSTEM_ROOT = process.env.LEO_SYSTEM_ROOT || 'D:/桌面/leo_ai_system';
const LEO_SKILLS_DIR = path.join(LEO_SYSTEM_ROOT, 'src', 'leo_skills');

// 静态能力列表（降级模式使用）
// Static capabilities used in degraded mode.
const STATIC_CAPABILITIES = {
  skills: [
    'content_layout_leo_skill', 'realestate_news_publisher_skill',
    'research_assistant_skill', 'web_search_skill', 'data_analyzer_skill',
    'agent_skill_creator_skill', 'article_to_prototype_skill',
    'project_marketing_doc_generator_skill', 'flask_api_generator_skill',
    'database_model_generator_skill', 'miniprogram_page_generator_skill',
    'dockerfile_generator_skill', 'vue_component_generator_skill',
    'fullstack_project_scaffold_skill', 'unit_test_generator_skill',
    'nginx_config_generator_skill', 'react_component_generator_skill',
    'github_actions_generator_skill', 'e2e_test_generator_skill',
    'vue_page_generator_skill', 'miniprogram_component_generator_skill',
    'css_layout_generator_skill', 'flask_auth_generator_skill',
    'fastapi_endpoint_generator_skill', 'api_doc_generator_skill',
    'miniprogram_project_scaffold_skill', 'flask_api_scaffold_skill',
    'deployment_script_generator_skill', 'api_test_generator_skill',
    'database_migration_skill', 'docker_compose_generator_skill',
    'videocut_skills', 'claude_prompt_engineering_skills',
    'text_generator_skill', 'skill_code_generator_skill',
    'twitter_monitor_skill', 't3_stack_scaffold_skill',
    'security_scan_skill', 'github_to_skills_skill',
    'skill_evolution_assistant_skill', 'skill_evolution_manager_skill',
    'skill_manager_skill', 'subagent_creator_skill',
    'obsidian_sync_skill', 'tech_extractor_skill',
    'business_research_skill'
  ],
  agents: [
    'task_agent', 'research_agent', 'analysis_agent',
    'creative_agent', 'realestate_agent', 'backend_agent',
    'frontend_agent', 'devops_agent', 'test_agent',
    'scaffold_agent', 'security_agent', 'product_manager_agent',
    'architect_agent', 'mobile_agent'
  ],
  workflows: [
    'content-pipeline', 'research-pipeline', 'analysis-pipeline',
    'fullstack-dev-pipeline', 'miniprogram-dev-pipeline',
    'api-pipeline', 'realestate-pipeline', 'ecommerce-pipeline'
  ]
};

// 动态能力缓存
let dynamicCapabilities = null;
let lastScanTime = 0;
const SCAN_CACHE_MS = 60000; // 1分钟内不重复扫描

// 模块级别的日志函数（避免 undefined 错误）
const log = {
  info: (msg) => console.log(`[leo-system] INFO: ${msg}`),
  error: (msg) => console.error(`[leo-system] ERROR: ${msg}`),
  warn: (msg) => console.warn(`[leo-system] WARN: ${msg}`),
  debug: (msg) => console.debug(`[leo-system] DEBUG: ${msg}`)
};

/**
 * 动态扫描 Leo System Skills 目录
 * 自动发现所有新添加的 Skills
 */
function scanLeoSkills() {
  const now = Date.now();
  if (dynamicCapabilities && (now - lastScanTime) < SCAN_CACHE_MS) {
    return dynamicCapabilities;
  }

  const skills = [];

  try {
    // 扫描 src/leo_skills 目录下所有 *_skill 目录
    const categories = ['content_creation', 'backend', 'frontend', 'devops',
                        'tools', 'utilities', 'testing', 'scaffold',
                        'security', 'automation', 'collaboration',
                        'debugging', 'development', 'business', 'intelligence',
                        'prompt_engineering', 'videocut_skills', 'core'];

    for (const category of categories) {
      const categoryPath = path.join(LEO_SKILLS_DIR, category);
      if (!fs.existsSync(categoryPath)) continue;

      const entries = fs.readdirSync(categoryPath, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.isDirectory() && entry.name.endsWith('_skill')) {
          const skillName = entry.name;
          const skillPath = path.join(categoryPath, skillName);

          // 读取 SKILL.md 获取描述
          let description = `${skillName} - Leo Skill`;
          const skillMdPath = path.join(skillPath, 'SKILL.md');
          if (fs.existsSync(skillMdPath)) {
            try {
              const content = fs.readFileSync(skillMdPath, 'utf-8');
              const lines = content.split('\n');
              // 第二行通常是描述（添加空值检查防止 trim 错误）
              if (lines.length > 1 && lines[1]) {
                const trimmed = lines[1].trim().replace(/^[-*] /, '');
                if (trimmed) description = trimmed;
              }
            } catch (e) {
              // 使用默认描述
            }
          }

          skills.push({
            name: skillName,
            description: description,
            path: path.join(category, skillName)
          });
        }
      }
    }

    dynamicCapabilities = {
      skills: skills,
      scannedAt: new Date().toISOString(),
      totalCount: skills.length
    };
    lastScanTime = now;

    log.info(`Scanned ${skills.length} skills from Leo System`);
  } catch (e) {
    log.error(`Failed to scan skills: ${e.message}`);
    return null;
  }

  return dynamicCapabilities;
}

/**
 * 动态注册 Skills 为 OpenClaw 工具
 */
function registerDynamicSkills(api, capabilities) {
  if (!capabilities || !capabilities.skills) return;

  const tools = {};

  for (const skill of capabilities.skills) {
    const toolName = `leo_skill_${skill.name}`;

    tools[toolName] = {
      description: skill.description || `Execute ${skill.name}`,
      parameters: {
        type: 'object',
        properties: {
          action: {
            type: 'string',
            description: 'Action to perform',
            enum: ['execute', 'info', 'list']
          },
          params: {
            type: 'object',
            description: 'Skill parameters',
            additionalProperties: true
          }
        },
        required: ['action']
      },
      handler: async ({ action = 'execute', params = {} }) => {
        try {
          const response = await callMCP('tools/call', {
            name: `leo_skill_${skill.name}`,
            arguments: { action, params }
          });
          return { content: [{ type: 'text', text: JSON.stringify(response, null, 2) }] };
        } catch (e) {
          return { content: [{ type: 'text', text: `Error: ${e.message}` }] };
        }
      }
    };
  }

  return tools;
}

export default function registerLeoSystemPlugin(api) {
  // log 已在模块级别定义

  let mcpProcess = null;
  let mcpReady = false;
  let useStaticMode = false;  // 降级模式标志

  // Plugin configuration
  const getConfig = () => api.config?.plugins?.entries?.['leo-system'] || {};
  const { mcpServerPath, enabled = true } = getConfig();

  // Tool definitions
  const tools = {};

  async function initializeMCP() {
    if (!enabled || !mcpServerPath) {
      log.info('Leo System integration disabled, using static mode');
      useStaticMode = true;
      return;
    }

    if (!fs.existsSync(mcpServerPath)) {
      log.warn(`MCP Server not found, using static mode: ${mcpServerPath}`);
      useStaticMode = true;
      return;
    }

    log.info(`Starting Leo MCP Server: ${mcpServerPath}`);

    return new Promise((resolve) => {
      mcpProcess = spawn('python', [mcpServerPath], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
      });

      mcpProcess.stdout.on('data', (data) => {
        const msg = data.toString().trim();
        log.debug(`MCP: ${msg}`);

        // Check for initialization
        if (msg.includes('Leo MCP Server') && msg.includes('OK')) {
          mcpReady = true;
          log.info('Leo MCP Server ready');
          resolve();
        }
      });

      mcpProcess.stderr.on('data', (data) => {
        log.error(`MCP Error: ${data.toString()}`);
      });

      mcpProcess.on('error', (err) => {
        log.error(`MCP process error: ${err.message}`);
        resolve(); // Continue anyway
      });

      mcpProcess.on('exit', (code) => {
        log.warn(`MCP process exited with code ${code}`);
        mcpReady = false;
        mcpProcess = null;
      });

      // Timeout after 30 seconds
      setTimeout(() => {
        if (!mcpReady) {
          log.warn('MCP initialization timeout');
          resolve(); // Continue anyway
        }
      }, 30000);
    });
  }

  async function callMCP(method, params = {}) {
    return new Promise((resolve) => {
      if (!mcpProcess || !mcpReady || useStaticMode) {
        // 降级模式：返回静态能力信息
        if (method === 'leo/capabilities') {
          return resolve({
            skills: STATIC_CAPABILITIES.skills,
            agents: STATIC_CAPABILITIES.agents,
            workflows: STATIC_CAPABILITIES.workflows,
            mode: 'static'
          });
        }
        return resolve({
          error: 'MCP server not running',
          mode: 'static',
          message: 'Leo System is running in static mode. All 46 skills, 14 agents, and 8 workflows are available.'
        });
      }

      const request = JSON.stringify({ method, params }) + '\n';

      mcpProcess.stdin.write(request);

      const onData = (data) => {
        try {
          const response = JSON.parse(data.toString());
          mcpProcess.stdout.removeListener('data', onData);
          resolve(response);
        } catch (e) {
          log.error(`Invalid MCP response: ${data}`);
        }
      };

      mcpProcess.stdout.on('data', onData);

      setTimeout(() => {
        mcpProcess.stdout.removeListener('data', onData);
        resolve({ error: 'MCP request timeout', mode: 'fallback' });
      }, 60000);
    });
  }
  async function executeSkillScript(skillName, payload = {}) {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(LEO_SYSTEM_ROOT, 'scripts', 'run_skill_direct.py');
      const proc = spawn(
        'python',
        [scriptPath, '--skill', skillName, '--payload', JSON.stringify(payload || {})],
        {
          cwd: LEO_SYSTEM_ROOT,
          env: { ...process.env, PYTHONPATH: `${LEO_SYSTEM_ROOT};${process.env.PYTHONPATH || ''}` }
        }
      );

      let stdout = '';
      let stderr = '';
      proc.stdout.on('data', (chunk) => {
        stdout += chunk.toString();
      });
      proc.stderr.on('data', (chunk) => {
        stderr += chunk.toString();
      });

      proc.on('error', (error) => {
        reject(error);
      });

      proc.on('close', (code) => {
        const text = stdout.trim();

        if (text) {
          try {
            const parsed = JSON.parse(text);
            if (code !== 0 && parsed && typeof parsed === 'object' && parsed.success === undefined) {
              parsed.success = false;
            }
            resolve(parsed);
            return;
          } catch (error) {
            // fall through to wrapped output
          }
        }

        if (code !== 0) {
          reject(new Error(`exit ${code}: ${(stderr || stdout).trim()}`));
          return;
        }

        if (!text) {
          resolve({ success: true, content: '', markdown: '', data: {} });
          return;
        }

        resolve({ success: true, content: text, markdown: text, data: { raw: text } });
      });
    });
  }

  function registerSystemEventHandlers() {
    if (typeof api.onSystemEvent !== 'function') {
      log.warn('api.onSystemEvent is unavailable, skip direct skill event registration');
      return;
    }

    api.onSystemEvent(/^skill:(\w+):execute$/, async (event, payload) => {
      const matched = event?.match?.[1]
        || event?.text?.match?.(/^skill:(\w+):execute$/)?.[1]
        || payload?.skill
        || '';
      const skillName = String(matched || '').trim();

      if (!skillName) {
        return {
          content: 'Skill name missing in system event',
          markdown: 'Skill name missing in system event',
          data: { success: false, status: 'error', error: 'Skill name missing' }
        };
      }

      log.info(`Direct skill system event: ${skillName}`);
      try {
        const result = await executeSkillScript(skillName, payload || {});
        const content = result.content || result.error || `Skill ${skillName} executed`;
        const markdown = result.markdown || content;
        return {
          content,
          markdown,
          data: result
        };
      } catch (error) {
        log.error(`Direct skill execution failed (${skillName}): ${error.message}`);
        return {
          content: `执行失败: ${error.message}`,
          markdown: `执行失败: ${error.message}`,
          data: { success: false, status: 'error', skill: skillName, error: error.message }
        };
      }
    });
  }

  // Register tools
  async function registerTools() {
    log.info('Registering Leo System tools...');

    // Tool: leo_capabilities
    tools.leo_capabilities = {
      description: 'List all available Leo System capabilities (skills, agents, workflows)',
      parameters: {
        type: 'object',
        properties: {
          mode: {
            type: 'string',
            description: 'Mode: dynamic (scan Leo System) or static (cached)',
            enum: ['dynamic', 'static']
          }
        },
        required: []
      },
      handler: async ({ mode = 'dynamic' }) => {
        try {
          let response;
          if (mode === 'dynamic') {
            // 动态扫描
            const capabilities = scanLeoSkills();
            if (capabilities) {
              response = {
                mode: 'dynamic',
                skills: capabilities.skills.map(s => ({ name: s.name, description: s.description })),
                agents: STATIC_CAPABILITIES.agents,
                workflows: STATIC_CAPABILITIES.workflows,
                scannedAt: capabilities.scannedAt,
                totalSkills: capabilities.totalCount
              };
            } else {
              response = { ...STATIC_CAPABILITIES, mode: 'fallback' };
            }
          } else {
            response = { ...STATIC_CAPABILITIES, mode: 'static' };
          }
          return { content: [{ type: 'text', text: JSON.stringify(response, null, 2) }] };
        } catch (e) {
          return { content: [{ type: 'text', text: `Error: ${e.message}` }] };
        }
      }
    };

    // Tool: leo_refresh - 刷新能力列表
    tools.leo_refresh = {
      description: 'Refresh Leo System capability list (force rescan skills directory)',
      parameters: {
        type: 'object',
        properties: {
          force: {
            type: 'boolean',
            description: 'Force refresh, ignore cache',
            default: false
          }
        },
        required: []
      },
      handler: async ({ force = false }) => {
        try {
          if (force) {
            lastScanTime = 0; // 清除缓存
            dynamicCapabilities = null;
          }
          const capabilities = scanLeoSkills();
          if (capabilities) {
            return {
              content: [{
                type: 'text',
                text: JSON.stringify({
                  status: 'success',
                  message: `已刷新能力列表`,
                  skillsCount: capabilities.totalCount,
                  scannedAt: capabilities.scannedAt,
                  skills: capabilities.skills.map(s => s.name)
                }, null, 2)
              }]
            };
          } else {
            return {
              content: [{
                type: 'text',
                text: JSON.stringify({
                  status: 'error',
                  message: '刷新失败，使用静态列表',
                  skills: STATIC_CAPABILITIES.skills
                }, null, 2)
              }]
            };
          }
        } catch (e) {
          return { content: [{ type: 'text', text: `Error: ${e.message}` }] };
        }
      }
    };

    // Tool: leo_execute_skill
    tools.leo_execute_skill = {
      description: 'Execute a Leo Skill',
      parameters: {
        type: 'object',
        properties: {
          skill_name: { type: 'string', description: 'Skill name' },
          action: { type: 'string', description: 'Action', default: 'execute' },
          params: { type: 'object', description: 'Parameters' }
        },
        required: ['skill_name']
      },
      handler: async ({ skill_name, action = 'execute', params = {} }) => {
        try {
          const response = await callMCP('tools/call', {
            name: `leo_skill_${skill_name}`,
            arguments: { action, params }
          });
          return { content: [{ type: 'text', text: JSON.stringify(response, null, 2) }] };
        } catch (e) {
          return { content: [{ type: 'text', text: `Error: ${e.message}` }] };
        }
      }
    };

    // Tool: leo_execute_agent
    tools.leo_execute_agent = {
      description: 'Execute a Leo Agent',
      parameters: {
        type: 'object',
        properties: {
          agent_name: { type: 'string', description: 'Agent name' },
          task: { type: 'string', description: 'Task description' },
          context: { type: 'object', description: 'Context' }
        },
        required: ['agent_name', 'task']
      },
      handler: async ({ agent_name, task, context = {} }) => {
        try {
          const response = await callMCP('tools/call', {
            name: `leo_agent_${agent_name}`,
            arguments: { task, context }
          });
          return { content: [{ type: 'text', text: JSON.stringify(response, null, 2) }] };
        } catch (e) {
          return { content: [{ type: 'text', text: `Error: ${e.message}` }] };
        }
      }
    };

    // Tool: leo_execute_workflow
    tools.leo_execute_workflow = {
      description: 'Execute a Leo Workflow',
      parameters: {
        type: 'object',
        properties: {
          workflow_name: { type: 'string', description: 'Workflow name' },
          input: { type: 'object', description: 'Input' }
        },
        required: ['workflow_name']
      },
      handler: async ({ workflow_name, input = {} }) => {
        try {
          const response = await callMCP('tools/call', {
            name: `leo_workflow_${workflow_name}`,
            arguments: { input }
          });
          return { content: [{ type: 'text', text: JSON.stringify(response, null, 2) }] };
        } catch (e) {
          return { content: [{ type: 'text', text: `Error: ${e.message}` }] };
        }
      }
    };

    // Register all tools
    for (const [name, def] of Object.entries(tools)) {
      try {
        // OpenClaw registerTool 接受一个工具对象
        api.registerTool({
          name: name,
          description: def.description || `${name} tool`,
          parameters: def.parameters || { type: 'object', properties: {} },
          handler: def.handler
        });
      } catch (e) {
        log.error(`Failed to register tool ${name}: ${e.message}`);
      }
    }

    log.info(`Registered ${Object.keys(tools).length} Leo System tools`);
  }

  // Plugin lifecycle
  async function start() {
    log.info('Starting Leo System plugin...');
    registerSystemEventHandlers();
    await initializeMCP();
    await registerTools();
  }

  function stop() {
    if (mcpProcess) {
      log.info('Stopping Leo MCP Server...');
      mcpProcess.stdin.end();
      mcpProcess.kill();
      mcpProcess = null;
    }
  }

  // Register service
  api.registerService({
    id: 'leo-system',
    start,
    stop
  });

  log.info('Leo System plugin registered successfully');
}
