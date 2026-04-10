#!/usr/bin/env python3
"""
跨平台工具检测模块 (Platform Utilities)

提供跨平台兼容的工具检测、路径解析等功能。
支持 macOS、Linux、Windows。

版本: v1.0.0
作者: Skills Health Guardian Team
"""

import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Tuple


def get_platform() -> str:
    """
    获取当前平台标识。
    
    Returns:
        'darwin' | 'linux' | 'win32'
    """
    return sys.platform


def is_macos() -> bool:
    """是否为 macOS 系统"""
    return sys.platform == 'darwin'


def is_linux() -> bool:
    """是否为 Linux 系统"""
    return sys.platform.startswith('linux')


def is_windows() -> bool:
    """是否为 Windows 系统"""
    return sys.platform == 'win32'


def find_chrome_path() -> Optional[str]:
    """
    跨平台查找 Chrome 可执行文件路径。
    
    Returns:
        Chrome 可执行文件的路径，如果未找到则返回 None
    """
    platform = get_platform()
    
    if is_macos():
        # macOS: 检查 Applications 目录
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    elif is_linux():
        # Linux: 检查常见安装路径
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
        ]
    elif is_windows():
        # Windows: 使用 shutil.which 自动查找 PATH
        chrome_executables = ["chrome.exe", "google-chrome.exe", "chromium.exe"]
        for exe in chrome_executables:
            path = shutil.which(exe)
            if path:
                return path
        return None
    else:
        return None
    
    # 检查路径是否存在（macOS/Linux）
    for path in chrome_paths:
        if Path(path).exists():
            return path
    
    return None


def check_chrome_installed() -> bool:
    """
    检查 Chrome 是否已安装。
    
    Returns:
        True 如果 Chrome 可用，否则 False
    """
    chrome_path = find_chrome_path()
    if not chrome_path:
        return False
    
    try:
        result = subprocess.run(
            [chrome_path, "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def get_chrome_version() -> Optional[str]:
    """
    获取 Chrome 版本号。
    
    Returns:
        版本字符串，如果获取失败则返回 None
    """
    chrome_path = find_chrome_path()
    if not chrome_path:
        return None
    
    try:
        result = subprocess.run(
            [chrome_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # 输出格式: "Google Chrome 123.0.6312.58"
            version = result.stdout.strip().split()[-1]
            return version
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError, IndexError):
        pass
    
    return None


def find_command(command: str) -> Optional[str]:
    """
    跨平台查找命令/可执行文件。
    
    Args:
        command: 命令名称（如 'python3', 'node', 'npm'）
    
    Returns:
        可执行文件的完整路径，如果未找到则返回 None
    """
    return shutil.which(command)


def check_command_available(command: str) -> bool:
    """
    检查命令是否可用。
    
    Args:
        command: 命令名称
    
    Returns:
        True 如果命令可用，否则 False
    """
    return find_command(command) is not None


def get_python_executable() -> str:
    """
    获取当前 Python 解释器路径。
    
    Returns:
        Python 可执行文件的绝对路径
    """
    return sys.executable


def normalize_path(path: str) -> Path:
    """
    标准化路径（处理跨平台路径分隔符）。
    
    Args:
        path: 原始路径字符串
    
    Returns:
        标准化后的 Path 对象
    """
    return Path(path).expanduser().resolve()


def get_home_directory() -> Path:
    """
    获取用户主目录。
    
    Returns:
        用户主目录的 Path 对象
    """
    return Path.home()


def get_config_directory(app_name: str = "skills-health-guardian") -> Path:
    """
    获取应用配置目录（遵循平台规范）。
    
    Args:
        app_name: 应用名称
    
    Returns:
        配置目录的 Path 对象
    
    Returns:
        - macOS: ~/Library/Application Support/<app_name>
        - Linux: ~/.config/<app_name>
        - Windows: %APPDATA%/<app_name>
    """
    if is_macos():
        config_dir = Path.home() / "Library" / "Application Support" / app_name
    elif is_windows():
        import os
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            config_dir = Path(appdata) / app_name
        else:
            # Fallback
            config_dir = Path.home() / ".config" / app_name
    else:  # Linux and others
        config_dir = Path.home() / ".config" / app_name
    
    return config_dir


def get_temp_directory() -> Path:
    """
    获取临时目录。
    
    Returns:
        临时目录的 Path 对象
    """
    return Path("/tmp" if not is_windows() else Path.home() / "AppData" / "Local" / "Temp")


def is_wsl() -> bool:
    """
    检查是否运行在 WSL (Windows Subsystem for Linux) 环境中。
    
    Returns:
        True 如果在 WSL 中运行，否则 False
    """
    if not is_linux():
        return False
    
    try:
        with open("/proc/version", "r") as f:
            version_info = f.read().lower()
            return "microsoft" in version_info
    except (FileNotFoundError, IOError):
        return False


def get_system_info() -> dict:
    """
    获取系统信息摘要。
    
    Returns:
        包含系统信息的字典
    """
    return {
        "platform": get_platform(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "executable": sys.executable,
        "is_macos": is_macos(),
        "is_linux": is_linux(),
        "is_windows": is_windows(),
        "is_wsl": is_wsl(),
        "chrome_installed": check_chrome_installed(),
        "chrome_version": get_chrome_version(),
    }


if __name__ == "__main__":
    # 测试代码
    print("=== 跨平台工具检测模块测试 ===\n")
    
    info = get_system_info()
    print("系统信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print(f"\nChrome 信息:")
    print(f"  已安装: {check_chrome_installed()}")
    print(f"  路径: {find_chrome_path()}")
    print(f"  版本: {get_chrome_version()}")
    
    print(f"\n配置目录: {get_config_directory()}")
    print(f"临时目录: {get_temp_directory()}")
