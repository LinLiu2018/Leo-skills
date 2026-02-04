# -*- coding: utf-8 -*-
"""
创建桌面快捷方式
"""
import os
import sys
from pathlib import Path

# 使用 winshell 或手动创建 .lnk
def create_shortcut():
    try:
        import win32com.client
    except ImportError:
        print("正在安装 pywin32...")
        os.system(f"{sys.executable} -m pip install pywin32 -q")
        import win32com.client

    # 获取桌面路径
    desktop = Path.home() / "Desktop"

    # 创建快捷方式
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(desktop / "启动大龙虾.lnk"))

    # 设置目标
    target = r"D:\桌面\leo_ai_system\scripts\一键启动大龙虾_带守护.bat"
    shortcut.TargetPath = target
    shortcut.WorkingDirectory = r"D:\桌面\leo_ai_system\scripts"
    shortcut.IconLocation = r"C:\Windows\System32\shell32.dll,13"
    shortcut.Description = "一键启动大龙虾网关 + 自动守护进程"

    shortcut.Save()
    print(f"✅ 快捷方式已创建: {desktop / '启动大龙虾.lnk'}")
    return True

if __name__ == "__main__":
    try:
        create_shortcut()
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        print("\n请手动创建快捷方式:")
        print("1. 右键点击桌面 → 新建 → 快捷方式")
        print("2. 输入位置: D:\桌面\leo_ai_system\scripts\一键启动大龙虾_带守护.bat")
        print("3. 命名为: 启动大龙虾")
        input("\n按回车键退出...")
