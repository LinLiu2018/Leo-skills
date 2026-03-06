#!/usr/bin/env bash
# Auto-Memory Hook - 自动记忆功能
# 功能：从会话中提取关键信息并保存到记忆库

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
MEMORY_DIR="${SCRIPT_DIR}/../memory"
SESSION_LOG="${MEMORY_DIR}/sessions/$(date '+%Y%m%d').log"

# 确保目录存在
mkdir -p "${MEMORY_DIR}/sessions"
mkdir -p "${MEMORY_DIR}/learnings"
mkdir -p "${MEMORY_DIR}/context"

# 获取会话ID
SESSION_ID="${CLAUDE_SESSION_ID:-$(date '+%s')}"

# 记录会话开始
echo "=== Session ${SESSION_ID} started at $(date) ===" >> "${SESSION_LOG}"

# 提取项目关键信息
extract_project_info() {
    local project_root="$1"

    # 检查项目类型
    if [ -f "${project_root}/package.json" ]; then
        echo "Project type: Node.js" >> "${MEMORY_DIR}/learnings/project-type.txt"
    elif [ -f "${project_root}/pyproject.toml" ]; then
        echo "Project type: Python" >> "${MEMORY_DIR}/learnings/project-type.txt"
    elif [ -f "${project_root}/Cargo.toml" ]; then
        echo "Project type: Rust" >> "${MEMORY_DIR}/learnings/project-type.txt"
    fi

    # 提取包管理信息
    if [ -f "${project_root}/package.json" ]; then
        local package_name=$(node -p "require('${project_root}/package.json').name" 2>/dev/null || echo "unknown")
        echo "Package: ${package_name}" >> "${MEMORY_DIR}/learnings/project-type.txt"
    fi
}

# 提取构建命令
extract_build_commands() {
    local project_root="$1"

    # Node.js
    if [ -f "${project_root}/package.json" ]; then
        node -p "JSON.stringify(require('${project_root}/package.json').scripts || {})" 2>/dev/null | \
            python3 -c "import json,sys; print('Build commands: ' + ', '.join(json.load(sys.stdin).keys()))" 2>/dev/null || true
    fi
}

# 记录工具使用模式
log_tool_usage() {
    local tool_name="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "${timestamp} - ${tool_name}" >> "${MEMORY_DIR}/learnings/tool-usage.log"
}

# 自动记忆功能
main() {
    # 尝试获取项目根目录
    local project_root="${CLAUDE_ROOT:-.}"

    if [ -d "${project_root}" ]; then
        extract_project_info "${project_root}"
        extract_build_commands "${project_root}"
    fi

    echo "Auto-memory updated at $(date)"
}

main "$@"
