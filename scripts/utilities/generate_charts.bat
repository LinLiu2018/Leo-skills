@echo off
REM 宁波商业地产租赁经纪商业计划书 - 图表生成脚本
REM 运行前请确保已安装 Python 和 matplotlib

echo ====================================
echo 生成商业计划书图表
echo ====================================

REM 创建charts目录
if not exist charts mkdir charts

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 未检测到Python，请先安装 Python 3.8+
    echo pip install matplotlib numpy
    pause
    exit /b 1
)

echo 📊 正在生成图表...

REM 运行Python脚本生成图表
python chart_generator.py

if errorlevel 1 (
    echo ❌ 图表生成失败
    pause
    exit /b 1
)

echo.
echo ====================================
echo ✅ 所有图表已生成完成！
echo ====================================
echo 📁 图表保存在: charts/
echo.
pause
