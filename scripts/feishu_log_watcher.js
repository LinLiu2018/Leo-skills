/**
 * 飞书对话日志监视器
 * 自动监控 OpenClaw Gateway 日志，实时记录所有飞书对话
 * 官方仓库: https://github.com/openclaw/openclaw
 *
 * 使用方法:
 * 1. 先启动 Gateway: node openclaw.mjs gateway --port 18789
 * 2. 再运行此脚本: node feishu_log_watcher.js
 *
 * 或使用 start_log_watcher.bat 启动
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const LOG_DIR = path.join(__dirname, '..', 'logs', 'feishu');
const LOG_FILE = path.join(LOG_DIR, 'dialogue_latest.md');
const STATE_FILE = path.join(LOG_DIR, '.watcher_state.json');

// 确保目录存在
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
}

// 状态管理
let state = {
    lastMessageTime: null,
    pendingMessage: null,
    userInfo: {}
};

/**
 * 加载状态
 */
function loadState() {
    if (fs.existsSync(STATE_FILE)) {
        try {
            state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
        } catch (e) {
            console.warn('[Watcher] 无法加载状态文件，将创建新的');
        }
    }
}

/**
 * 保存状态
 */
function saveState() {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
}

/**
 * 获取当前时间
 */
function getTimestamp() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
}

/**
 * 获取今日日志文件名
 */
function getTodayLogFile() {
    const now = new Date();
    const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    return path.join(LOG_DIR, `dialogue_${dateStr}.md`);
}

/**
 * 记录对话
 */
function recordDialogue(data) {
    const logFile = getTodayLogFile();
    const timestamp = getTimestamp();

    const chatTypeLabel = data.chatType === 'p2p' ? '私聊' : '群聊';

    const logEntry = `## ${timestamp} | ${chatTypeLabel} | ${data.userName || data.userId}

**用户**: ${data.userName || data.userId}
**会话**: ${data.chatId}
**消息**: ${data.message}
**上下文**: ${data.contextUsage || 'N/A'}
**Token**: ${data.tokens || 'N/A'}

${data.response ? `**回复**: ${data.response.substring(0, 300)}${data.response.length > 300 ? '...' : ''}` : ''}

---

`;

    fs.appendFileSync(logFile, logEntry, 'utf8');

    // 同时更新 latest 文件（方便快速查看）
    fs.writeFileSync(LOG_FILE, logEntry, 'utf8');

    console.log(`[${timestamp}] 📝 已记录: ${chatTypeLabel} | ${data.userName || data.userId}: ${data.message.substring(0, 30)}...`);

    // 重置状态
    state.pendingMessage = null;
    saveState();
}

/**
 * 解析日志行
 */
function parseLogLine(line) {
    // 匹配收到消息: received message from USER_ID in CHAT_ID (chat_type)
    const receiveMatch = line.match(/received message from ([^\s]+) in ([^\s]+) \((p2p|group)\)/);
    if (receiveMatch) {
        return {
            type: 'receive',
            userId: receiveMatch[1],
            chatId: receiveMatch[2],
            chatType: receiveMatch[3]
        };
    }

    // 匹配发送回复: deliver called: text=...
    const deliverMatch = line.match(/deliver called: text=(.+)/);
    if (deliverMatch) {
        return {
            type: 'deliver',
            response: deliverMatch[1].trim()
        };
    }

    // 匹配上下文使用: Context: XXk/YYk (ZZ%)
    const contextMatch = line.match(/Context:\s*([\d.]+)k\/([\d.]+)k\s*\((\d+)%\)/);
    if (contextMatch) {
        return {
            type: 'context',
            contextUsage: `${contextMatch[1]}k/${contextMatch[2]}k (${contextMatch[3]}%)`
        };
    }

    // 匹配Token使用: Usage: XXh
    const usageMatch = line.match(/Usage:\s*([\d.]+[hm])/);
    if (usageMatch) {
        return {
            type: 'usage',
            tokens: usageMatch[1]
        };
    }

    return null;
}

/**
 * 处理日志行
 */
function processLogLine(line) {
    const parsed = parseLogLine(line);
    if (!parsed) return;

    const now = Date.now();

    switch (parsed.type) {
        case 'receive':
            // 新消息到达
            state.pendingMessage = {
                userId: parsed.userId,
                chatId: parsed.chatId,
                chatType: parsed.chatType,
                message: '',
                response: null,
                contextUsage: null,
                tokens: null
            };
            state.lastMessageTime = now;
            break;

        case 'deliver':
            // 机器人回复
            if (state.pendingMessage) {
                state.pendingMessage.response = parsed.response;
                // 延迟一下再记录，等待上下文信息
                setTimeout(() => {
                    if (state.pendingMessage && state.pendingMessage.response) {
                        recordDialogue(state.pendingMessage);
                    }
                }, 500);
            }
            break;

        case 'context':
            // 上下文使用
            if (state.pendingMessage) {
                state.pendingMessage.contextUsage = parsed.contextUsage;
            }
            break;

        case 'usage':
            // Token使用
            if (state.pendingMessage) {
                state.pendingMessage.tokens = parsed.tokens;
            }
            break;
    }
}

/**
 * 启动日志监视器
 */
async function startWatcher() {
    console.log('\n飞书对话日志监视器 v1.0\n');
    console.log('官方仓库: https://github.com/openclaw/openclaw');
    console.log(`日志目录: ${LOG_DIR}`);
    console.log(`日志文件: ${path.basename(getTodayLogFile())}`);
    console.log('\n等待对话...\n');

    loadState();

    // 启动Gateway并监视输出 (OpenClaw 官方仓库: github.com/openclaw/openclaw)
    const gateway = spawn('node', ['openclaw.mjs', 'gateway', '--port', '18789'], {
        cwd: 'D:\\moltbot',  // 目录名保持 moltbot，项目已重命名为 openclaw
        stdio: ['pipe', 'pipe', 'pipe']
    });

    gateway.stdout.on('data', (data) => {
        const lines = data.toString().split('\n');
        lines.forEach(line => {
            if (line.trim()) {
                processLogLine(line);
            }
        });
    });

    gateway.stderr.on('data', (data) => {
        const lines = data.toString().split('\n');
        lines.forEach(line => {
            if (line.trim()) {
                processLogLine(line);
            }
        });
    });

    gateway.on('close', (code) => {
        console.log(`\n⚠️ Gateway 已关闭 (code: ${code})`);
        process.exit(0);
    });

    gateway.on('error', (err) => {
        console.error(`\n❌ Gateway 启动失败: ${err.message}`);
        process.exit(1);
    });

    // 定期保存状态
    setInterval(saveState, 5000);
}

// 优雅关闭
process.on('SIGINT', () => {
    console.log('\n\n👋 监视器已停止');
    saveState();
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n\n👋 监视器已停止');
    saveState();
    process.exit(0);
});

// 启动
startWatcher();
