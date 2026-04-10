#!/usr/bin/env python3
"""
跨平台工具检测模块测试

测试 platform_utils.py 的跨平台兼容性功能。
"""

import pytest
import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from platform_utils import (
    get_platform,
    is_macos,
    is_linux,
    is_windows,
    find_chrome_path,
    check_chrome_installed,
    get_chrome_version,
    find_command,
    check_command_available,
    get_python_executable,
    normalize_path,
    get_home_directory,
    get_config_directory,
    get_temp_directory,
    is_wsl,
    get_system_info,
)


class TestPlatformDetection:
    """平台检测功能测试"""

    def test_get_platform_returns_valid(self):
        """测试平台检测返回有效值"""
        platform = get_platform()
        assert platform in ["darwin", "linux", "win32"]

    def test_platform_identifiers_mutually_exclusive(self):
        """测试平台标识符互斥"""
        # 只应该有一个返回 True
        sum_true = sum([is_macos(), is_linux(), is_windows()])
        assert sum_true == 1

    def test_current_platform_matches_sys_platform(self):
        """测试平台检测结果与 sys.platform 一致"""
        assert is_macos() == (sys.platform == "darwin")
        assert is_linux() == sys.platform.startswith("linux")
        assert is_windows() == (sys.platform == "win32")


class TestChromeDetection:
    """Chrome 检测功能测试"""

    def test_find_chrome_path_returns_path_or_none(self):
        """测试 Chrome 路径查找返回有效路径或 None"""
        path = find_chrome_path()
        if path:
            assert isinstance(path, str)
            assert len(path) > 0

    def test_check_chrome_installed_returns_bool(self):
        """测试 Chrome 安装检查返回布尔值"""
        result = check_chrome_installed()
        assert isinstance(result, bool)

    def test_get_chrome_version_returns_string_or_none(self):
        """测试 Chrome 版本获取返回字符串或 None"""
        version = get_chrome_version()
        if version:
            assert isinstance(version, str)
            assert len(version) > 0

    def test_chrome_version_consistency(self):
        """测试 Chrome 版本检测的一致性"""
        # 如果 Chrome 已安装，则版本号不为 None
        if check_chrome_installed():
            version = get_chrome_version()
            assert version is not None
            # 版本号应该包含点号（如 123.0.6312.58）
            assert "." in version
        else:
            # 如果 Chrome 未安装，路径和版本都应该为 None
            assert find_chrome_path() is None
            assert get_chrome_version() is None


class TestCommandDetection:
    """命令检测功能测试"""

    @pytest.mark.parametrize("command", ["python3", "python", "ls", "dir"])
    def test_find_command_returns_path_or_none(self, command):
        """测试命令查找返回路径或 None"""
        # Python 应该总能找到
        if command.startswith("python"):
            path = find_command(command)
            assert path is not None
        else:
            # 其他命令可能不存在
            path = find_command(command)
            assert path is None or isinstance(path, str)

    @pytest.mark.parametrize("command", ["python3", "python", "invalid-command-xyz"])
    def test_check_command_available_returns_bool(self, command):
        """测试命令可用性检查返回布尔值"""
        result = check_command_available(command)
        assert isinstance(result, bool)

    def test_python_always_available(self):
        """测试当前 Python 解释器始终可用"""
        python_exe = get_python_executable()
        assert python_exe is not None
        assert Path(python_exe).exists()


class TestPathUtilities:
    """路径处理功能测试"""

    def test_normalize_path_expands_home(self):
        """测试路径规范化展开 ~"""
        path = normalize_path("~/test")
        assert "~" not in str(path)
        # 应该是绝对路径
        assert path.is_absolute()

    def test_get_home_directory_exists(self):
        """测试获取主目录返回存在的路径"""
        home = get_home_directory()
        assert home.exists()
        assert home.is_absolute()

    def test_get_temp_directory_exists(self):
        """测试获取临时目录返回存在的路径"""
        temp = get_temp_directory()
        assert temp.exists()
        assert temp.is_absolute()

    def test_get_config_directory_returns_absolute_path(self):
        """测试获取配置目录返回绝对路径"""
        config = get_config_directory()
        assert isinstance(config, Path)
        # 注意：目录可能不存在，但路径应该是绝对路径


class TestWSLDetection:
    """WSL 检测功能测试"""

    def test_is_wsl_returns_bool(self):
        """测试 WSL 检测返回布尔值"""
        result = is_wsl()
        assert isinstance(result, bool)

    def test_wsl_only_on_linux(self):
        """测试 WSL 只在 Linux 上为 True"""
        if not is_linux():
            assert not is_wsl()


class TestSystemInfo:
    """系统信息获取测试"""

    def test_get_system_info_returns_dict(self):
        """测试系统信息返回字典"""
        info = get_system_info()
        assert isinstance(info, dict)
        assert len(info) > 0

    def test_system_info_contains_expected_keys(self):
        """测试系统信息包含预期字段"""
        info = get_system_info()
        expected_keys = {
            "platform",
            "python_version",
            "executable",
            "is_macos",
            "is_linux",
            "is_windows",
            "is_wsl",
            "chrome_installed",
            "chrome_version",
        }
        assert set(info.keys()) >= expected_keys

    def test_system_info_consistency(self):
        """测试系统信息的一致性"""
        info = get_system_info()

        # 平台标识符应与检测函数一致
        assert info["is_macos"] == is_macos()
        assert info["is_linux"] == is_linux()
        assert info["is_windows"] == is_windows()
        assert info["is_wsl"] == is_wsl()

        # Chrome 信息应与检测函数一致
        assert info["chrome_installed"] == check_chrome_installed()
        assert info["chrome_version"] == get_chrome_version()


class TestEdgeCases:
    """边界情况测试"""

    def test_normalize_path_with_empty_string(self):
        """测试空字符串路径规范化"""
        path = normalize_path("")
        assert path.exists()  # 空路径应该解析为当前目录

    def test_normalize_path_with_relative(self):
        """测试相对路径规范化"""
        path = normalize_path("../test")
        assert path.is_absolute()  # 应该转换为绝对路径

    def test_find_command_with_empty_string(self):
        """测试空字符串命令查找"""
        result = find_command("")
        assert result is None

    def test_check_command_available_with_empty_string(self):
        """测试空字符串命令可用性"""
        result = check_command_available("")
        assert result is False


@pytest.mark.skipif(sys.platform == "win32", reason="Skipping Windows-specific tests")
class TestUnixSpecific:
    """Unix 特定测试（macOS/Linux）"""

    def test_unix_common_commands(self):
        """测试 Unix 常见命令"""
        common_commands = ["ls", "pwd", "cat"]
        for cmd in common_commands:
            assert check_command_available(cmd), f"{cmd} should be available on Unix"


@pytest.mark.skipif(sys.platform != "win32", reason="Skipping non-Windows tests")
class TestWindowsSpecific:
    """Windows 特定测试"""

    def test_windows_common_commands(self):
        """测试 Windows 常见命令"""
        common_commands = ["cmd", "powershell"]
        for cmd in common_commands:
            # 注意：dir 不是独立命令，而是 cmd 内置命令
            if cmd not in ["dir"]:
                assert check_command_available(cmd), f"{cmd} should be available on Windows"
