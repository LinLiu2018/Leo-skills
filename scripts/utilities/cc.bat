@echo off
REM Leo AI System - 多模型切换工具 (cc)
REM 使用方法: cc switch <model_name>
REM 支持模型: claude, kimi, minimax, deepseek

setlocal enabledelayedexpansion

set "COMMAND=%1"
set "MODEL=%2"
set "CONFIG_DIR=%USERPROFILE%\.leo_ai"
set "CONFIG_FILE=%CONFIG_DIR%\model_config.json"

REM 创建配置目录
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

REM 主命令分发
if "%COMMAND%"=="switch" goto :switch
if "%COMMAND%"=="list" goto :list
if "%COMMAND%"=="current" goto :current
if "%COMMAND%"=="config" goto :config
if "%COMMAND%"=="help" goto :help
if "%COMMAND%"=="" goto :help

echo ❌ 未知命令: %COMMAND%
goto :help

:switch
if "%MODEL%"=="" (
    echo ❌ 请指定模型名称
    echo 使用方法: cc switch ^<model_name^>
    goto :list
)

REM 模型切换逻辑
if /i "%MODEL%"=="claude" goto :switch_claude
if /i "%MODEL%"=="sonnet" goto :switch_claude
if /i "%MODEL%"=="kimi" goto :switch_kimi
if /i "%MODEL%"=="minimax" goto :switch_minimax
if /i "%MODEL%"=="deepseek" goto :switch_deepseek
if /i "%MODEL%"=="haiku" goto :switch_haiku
if /i "%MODEL%"=="opus" goto :switch_opus

echo ❌ 不支持的模型: %MODEL%
goto :list

:switch_claude
echo 🔄 切换到 Claude 3.5 Sonnet...
echo {"current_model": "claude-3-5-sonnet", "provider": "anthropic"} > "%CONFIG_FILE%"
echo ✅ 已切换到 Claude 3.5 Sonnet
echo 💡 重启 Claude Code 生效: claude
goto :end

:switch_haiku
echo 🔄 切换到 Claude 3.5 Haiku (快速模式)...
echo {"current_model": "claude-3-5-haiku", "provider": "anthropic"} > "%CONFIG_FILE%"
echo ✅ 已切换到 Claude 3.5 Haiku
echo 💡 特点: 速度最快,成本最低
echo 💡 重启 Claude Code 生效: claude --model haiku
goto :end

:switch_opus
echo 🔄 切换到 Claude Opus 4.5 (最强模式)...
echo {"current_model": "claude-opus-4-5", "provider": "anthropic"} > "%CONFIG_FILE%"
echo ✅ 已切换到 Claude Opus 4.5
echo 💡 特点: 推理能力最强,适合复杂任务
echo 💡 重启 Claude Code 生效: claude --model opus
goto :end

:switch_kimi
echo 🔄 切换到 Kimi 2.5 (Moonshot)...
echo 📝 需要配置 API Key
if not exist "%CONFIG_DIR%\kimi_api_key.txt" (
    echo ❌ 未找到 Kimi API Key
    echo 💡 请创建文件: %CONFIG_DIR%\kimi_api_key.txt
    echo 💡 并填入你的 Kimi API Key
    echo 💡 获取地址: https://platform.moonshot.cn/
    goto :end
)
echo {"current_model": "moonshot-v1-128k", "provider": "kimi", "api_base": "https://api.moonshot.cn/v1"} > "%CONFIG_FILE%"
echo ✅ 已切换到 Kimi 2.5
echo 💡 特点: 128K 超长上下文,中文优化
echo ⚠️  注意: 需要使用支持 OpenAI 兼容接口的客户端
goto :end

:switch_minimax
echo 🔄 切换到 MiniMax 2.1...
echo 📝 需要配置 API Key
if not exist "%CONFIG_DIR%\minimax_api_key.txt" (
    echo ❌ 未找到 MiniMax API Key
    echo 💡 请创建文件: %CONFIG_DIR%\minimax_api_key.txt
    echo 💡 并填入你的 MiniMax API Key
    echo 💡 获取地址: https://www.minimaxi.com/
    goto :end
)
echo {"current_model": "abab6.5-chat", "provider": "minimax", "api_base": "https://api.minimax.chat/v1"} > "%CONFIG_FILE%"
echo ✅ 已切换到 MiniMax 2.1
echo 💡 特点: 国产大模型,性价比高
echo ⚠️  注意: 需要使用支持 OpenAI 兼容接口的客户端
goto :end

:switch_deepseek
echo 🔄 切换到 DeepSeek V3...
echo 📝 需要配置 API Key
if not exist "%CONFIG_DIR%\deepseek_api_key.txt" (
    echo ❌ 未找到 DeepSeek API Key
    echo 💡 请创建文件: %CONFIG_DIR%\deepseek_api_key.txt
    echo 💡 并填入你的 DeepSeek API Key
    echo 💡 获取地址: https://platform.deepseek.com/
    goto :end
)
echo {"current_model": "deepseek-chat", "provider": "deepseek", "api_base": "https://api.deepseek.com/v1"} > "%CONFIG_FILE%"
echo ✅ 已切换到 DeepSeek V3
echo 💡 特点: 代码能力强,价格便宜
echo ⚠️  注意: 需要使用支持 OpenAI 兼容接口的客户端
goto :end

:list
echo.
echo 📋 支持的模型列表:
echo.
echo Claude 系列 (Anthropic):
echo   - claude / sonnet  : Claude 3.5 Sonnet (默认,平衡性能)
echo   - haiku           : Claude 3.5 Haiku (快速,便宜)
echo   - opus            : Claude Opus 4.5 (最强,最贵)
echo.
echo 国产模型:
echo   - kimi            : Kimi 2.5 (Moonshot, 128K 上下文)
echo   - minimax         : MiniMax 2.1 (性价比高)
echo   - deepseek        : DeepSeek V3 (代码能力强)
echo.
echo 使用方法: cc switch ^<model_name^>
echo 示例: cc switch kimi
goto :end

:current
if exist "%CONFIG_FILE%" (
    echo 📌 当前模型配置:
    type "%CONFIG_FILE%"
) else (
    echo ℹ️  未设置模型,使用默认: Claude 3.5 Sonnet
)
goto :end

:config
echo 📁 配置目录: %CONFIG_DIR%
echo.
if exist "%CONFIG_FILE%" (
    echo 📄 当前配置:
    type "%CONFIG_FILE%"
    echo.
)
echo 📝 API Key 文件:
if exist "%CONFIG_DIR%\kimi_api_key.txt" (
    echo   ✅ Kimi API Key 已配置
) else (
    echo   ❌ Kimi API Key 未配置
)
if exist "%CONFIG_DIR%\minimax_api_key.txt" (
    echo   ✅ MiniMax API Key 已配置
) else (
    echo   ❌ MiniMax API Key 未配置
)
if exist "%CONFIG_DIR%\deepseek_api_key.txt" (
    echo   ✅ DeepSeek API Key 已配置
) else (
    echo   ❌ DeepSeek API Key 未配置
)
goto :end

:help
echo.
echo 🤖 Leo AI System - 多模型切换工具
echo.
echo 使用方法:
echo   cc switch ^<model^>  - 切换模型
echo   cc list            - 列出所有支持的模型
echo   cc current         - 显示当前模型
echo   cc config          - 显示配置信息
echo   cc help            - 显示帮助信息
echo.
echo 示例:
echo   cc switch claude   - 切换到 Claude 3.5 Sonnet
echo   cc switch kimi     - 切换到 Kimi 2.5
echo   cc switch minimax  - 切换到 MiniMax 2.1
echo.
goto :end

:end
endlocal
