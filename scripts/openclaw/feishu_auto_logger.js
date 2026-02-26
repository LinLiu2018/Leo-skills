/**
 * 飞书对话自动日志系统
 * 自动记录所有飞书对话到日志文件
 */

const fs = require('fs');
const path = require('path');

// 配置
const LOG_DIR = path.join(__dirname, '..', 'logs', 'feishu');
const DAILY_LOG_FILE = (date) => path.join(LOG_DIR, `dialogue_${date}.md`);
const INDEX_FILE = path.join(LOG_DIR, 'index.md');

// 确保目录存在
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
}

/**
 * 格式化时间
 */
function formatTime(date) {
    return date.toISOString().replace('T', ' ').substring(0, 19);
}

/**
 * 获取今日日期字符串
 */
function getTodayDate() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}

/**
 * 记录对话到每日日志
 */
function logDialogue(data) {
    const {
        userId,
        userName,
        chatType, // 'p2p' or 'group'
        chatId,
        message,
        response,
        model,
        contextUsage,
        tokens
    } = data;

    const timestamp = formatTime(new Date());
    const date = getTodayDate();
    const logFile = DAILY_LOG_FILE(date);

    // 构建日志条目
    const logEntry = `## ${timestamp} | ${chatType === 'p2p' ? '私聊' : '群聊'} | ${userName || userId}

**用户**: ${userName || userId}
**消息**: ${message}
**上下文**: ${contextUsage || 'N/A'}
**Token**: ${tokens || 'N/A'}

${response ? `**回复**: ${response}` : ''}

---

`;

    // 追加到日志文件
    fs.appendFileSync(logFile, logEntry, 'utf8');

    // 更新索引
    updateIndex(date, chatType, userName || userId, message);

    console.log(`[日志] 已记录对话到 ${logFile}`);
}

/**
 * 更新索引文件
 */
function updateIndex(date, chatType, user, message) {
    const shortMsg = message.substring(0, 50) + (message.length > 50 ? '...' : '');
    const indexEntry = `- ${date} | ${chatType === 'p2p' ? '私聊' : '群聊'} | ${user}: ${shortMsg}`;

    let indexContent = '';
    if (fs.existsSync(INDEX_FILE)) {
        indexContent = fs.readFileSync(INDEX_FILE, 'utf8');
    }

    // 检查今日是否已有记录
    const todaySection = `## ${date}`;
    if (indexContent.includes(todaySection)) {
        // 已有今日记录，追加
        const lines = indexContent.split('\n');
        let foundToday = false;
        let result = [];
        for (let line of lines) {
            if (line.startsWith('## ') && !foundToday) {
                if (line === todaySection) {
                    foundToday = true;
                }
            }
            if (foundToday && line.startsWith('- ')) {
                continue; // 跳过旧的今日记录，稍后重新添加
            }
            if (foundToday && line.startsWith('## ') && line !== todaySection) {
                foundToday = false;
            }
            result.push(line);
        }
        indexContent = result.filter(l => l.trim() !== '').join('\n') + '\n' + indexEntry + '\n';
    } else {
        // 新日期，添加到顶部
        indexContent = `${todaySection}\n\n${indexEntry}\n\n${indexContent}`;
    }

    fs.writeFileSync(INDEX_FILE, indexContent, 'utf8');
}

/**
 * 记录系统事件
 */
function logEvent(eventType, details) {
    const timestamp = formatTime(new Date());
    const date = getTodayDate();
    const logFile = DAILY_LOG_FILE(date);

    const logEntry = `### ${timestamp} | ${eventType}

${JSON.stringify(details, null, 2)}

---

`;

    fs.appendFileSync(logFile, logEntry, 'utf8');
    console.log(`[事件] ${eventType}: ${JSON.stringify(details)}`);
}

/**
 * 生成统计报告
 */
function generateStats(date) {
    const logFile = DAILY_LOG_FILE(date);
    if (!fs.existsSync(logFile)) {
        return null;
    }

    const content = fs.readFileSync(logFile, 'utf8');
    const entries = content.split('---').filter(e => e.trim());

    let p2pCount = 0;
    let groupCount = 0;
    let totalMessages = 0;

    entries.forEach(entry => {
        if (entry.includes('私聊')) p2pCount++;
        if (entry.includes('群聊')) groupCount++;
        if (entry.includes('**消息**')) totalMessages++;
    });

    return {
        date,
        totalEntries: entries.length,
        p2pCount,
        groupCount,
        totalMessages
    };
}

// 导出模块
module.exports = {
    logDialogue,
    logEvent,
    generateStats,
    LOG_DIR,
    DAILY_LOG_FILE,
    getTodayDate
};

// 如果直接运行，生成今日统计
if (require.main === module) {
    const stats = generateStats(getTodayDate());
    if (stats) {
        console.log('\n📊 今日对话统计:');
        console.log(`  总对话: ${stats.totalEntries}`);
        console.log(`  私聊: ${stats.p2pCount}`);
        console.log(`  群聊: ${stats.groupCount}`);
        console.log(`  消息: ${stats.totalMessages}`);
    } else {
        console.log('今日暂无对话记录');
    }
}
