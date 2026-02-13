"""
浏览器配置管理模块

提供浏览器驱动路径、代理等设置的持久化存储和读取功能
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ...utils import logger


class BrowserConfig:
    """浏览器配置管理器"""

    DEFAULT_CONFIG_DIR = ".oh-my-mcp"
    DEFAULT_CONFIG_FILE = "browser_config.json"

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，默认为用户目录下的 ~/.oh-my-mcp/
        """
        if config_path is None:
            # 默认配置文件位置：~/.oh-my-mcp/
            config_dir = Path.home() / self.DEFAULT_CONFIG_DIR
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / self.DEFAULT_CONFIG_FILE
        else:
            self.config_path = Path(config_path)

        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """从配置文件加载配置"""
        # 先尝试迁移旧配置
        self._migrate_old_config()

        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                logger.info(f"Loaded browser configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load browser config from {self.config_path}: {e}")
                self._config = {}
        else:
            logger.debug(f"No browser config file found at {self.config_path}, using defaults")
            self._config = {}

    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存配置
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)

            # 设置文件权限（仅所有者可读写）
            if os.name != "nt":  # Unix/Linux/macOS
                os.chmod(self.config_path, 0o600)

            logger.info(f"Saved browser configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save browser config to {self.config_path}: {e}")
            raise

    def _migrate_old_config(self) -> None:
        """迁移旧的配置文件到新位置"""
        # 旧配置路径列表（按优先级）
        old_paths = [
            Path.home() / "oh-my-mcp" / self.DEFAULT_CONFIG_FILE,  # ~/oh-my-mcp/
            Path.home() / ".browser_config.json",  # 最早的单文件配置
        ]

        # 如果新配置已存在，不需要迁移
        if self.config_path.exists():
            return

        # 尝试从旧路径迁移
        for old_config_path in old_paths:
            if old_config_path.exists():
                try:
                    import shutil

                    # 确保目录存在
                    self.config_path.parent.mkdir(parents=True, exist_ok=True)
                    # 复制配置文件
                    shutil.copy2(old_config_path, self.config_path)
                    logger.info(
                        f"Migrated browser config from {old_config_path} to {self.config_path}"
                    )
                    # 删除旧配置文件
                    old_config_path.unlink()
                    logger.info(f"Removed old config file: {old_config_path}")
                    return  # 迁移成功，退出循环
                except Exception as e:
                    logger.warning(
                        f"Failed to migrate old browser config from {old_config_path}: {e}"
                    )

    def get_chrome_driver_path(self) -> Optional[str]:
        """
        获取 ChromeDriver 路径

        优先级：环境变量 CHROME_DRIVER_PATH > 配置文件 > None

        Returns:
            ChromeDriver 路径，如果未配置则返回 None
        """
        # 首先检查环境变量
        env_path = os.getenv("CHROME_DRIVER_PATH", "").strip()
        if env_path:
            return env_path

        # 然后检查配置文件
        driver_paths = self._config.get("driver_paths", {})
        chrome_path = driver_paths.get("chrome")
        return str(chrome_path) if chrome_path else None

    def get_edge_driver_path(self) -> Optional[str]:
        """
        获取 EdgeDriver 路径

        优先级：环境变量 EDGE_DRIVER_PATH > 配置文件 > None

        Returns:
            EdgeDriver 路径，如果未配置则返回 None
        """
        # 首先检查环境变量
        env_path = os.getenv("EDGE_DRIVER_PATH", "").strip()
        if env_path:
            return env_path

        # 然后检查配置文件
        driver_paths = self._config.get("driver_paths", {})
        edge_path = driver_paths.get("edge")
        return str(edge_path) if edge_path else None

    def get_default_browser(self) -> str:
        """
        获取默认浏览器

        Returns:
            默认浏览器类型，默认为 "chrome"
        """
        return str(self._config.get("default_browser", "chrome"))

    def get_default_headless(self) -> bool:
        """
        获取默认无头模式配置

        Returns:
            是否默认使用无头模式，默认为 False
        """
        return bool(self._config.get("default_headless", False))

    def get_proxy(self) -> Optional[str]:
        """
        获取代理服务器配置

        优先级：环境变量 HTTPS_PROXY/HTTP_PROXY > 配置文件 > None

        Returns:
            代理服务器 URL，如果未配置则返回 None
        """
        # 检查环境变量
        proxy = (
            os.getenv("HTTPS_PROXY")
            or os.getenv("HTTP_PROXY")
            or os.getenv("https_proxy")
            or os.getenv("http_proxy")
        )
        if proxy:
            return proxy.strip()

        # 检查配置文件
        return self._config.get("proxy")

    def get_auto_fallback_enabled(self) -> bool:
        """
        获取是否启用 Chrome 到 Edge 的自动兜底

        Returns:
            是否启用自动兜底，默认为 True
        """
        return bool(self._config.get("auto_fallback", True))

    def get_screenshot_dir(self) -> Optional[str]:
        """
        获取截图保存目录

        Returns:
            截图保存目录路径，如果未配置则返回 None
        """
        return self._config.get("screenshot_dir")

    def get_screenshot_dir_path(self) -> Optional[Path]:
        """
        获取截图保存目录的 Path 对象

        如果配置了目录，会自动创建该目录

        Returns:
            截图保存目录的 Path 对象，如果未配置则返回 None
        """
        dir_path = self.get_screenshot_dir()
        if dir_path:
            path = Path(dir_path).expanduser()
            path.mkdir(parents=True, exist_ok=True)
            return path
        return None

    def set_chrome_driver_path(self, path: str) -> None:
        """
        设置 ChromeDriver 路径

        Args:
            path: ChromeDriver 可执行文件的完整路径
        """
        if "driver_paths" not in self._config:
            self._config["driver_paths"] = {}
        self._config["driver_paths"]["chrome"] = path
        self._save_config()

    def set_edge_driver_path(self, path: str) -> None:
        """
        设置 EdgeDriver 路径

        Args:
            path: EdgeDriver 可执行文件的完整路径
        """
        if "driver_paths" not in self._config:
            self._config["driver_paths"] = {}
        self._config["driver_paths"]["edge"] = path
        self._save_config()

    def set_default_browser(self, browser: str) -> None:
        """
        设置默认浏览器

        Args:
            browser: 浏览器类型 ("chrome" 或 "edge")
        """
        if browser not in ("chrome", "edge"):
            raise ValueError(f"Invalid browser type: {browser}. Must be 'chrome' or 'edge'")
        self._config["default_browser"] = browser
        self._save_config()

    def set_default_headless(self, headless: bool) -> None:
        """
        设置默认无头模式

        Args:
            headless: 是否默认使用无头模式
        """
        self._config["default_headless"] = headless
        self._save_config()

    def set_proxy(self, proxy: str) -> None:
        """
        设置代理服务器

        Args:
            proxy: 代理服务器 URL（如 "http://proxy.example.com:8080"）
        """
        self._config["proxy"] = proxy
        self._save_config()

    def set_auto_fallback(self, enabled: bool) -> None:
        """
        设置是否启用 Chrome 到 Edge 的自动兜底

        Args:
            enabled: 是否启用自动兜底
        """
        self._config["auto_fallback"] = enabled
        self._save_config()

    def set_screenshot_dir(self, dir_path: str) -> None:
        """
        设置截图保存目录

        Args:
            dir_path: 截图保存目录路径
        """
        # 验证路径格式
        path = Path(dir_path).expanduser()
        # 尝试创建目录以验证路径有效性
        path.mkdir(parents=True, exist_ok=True)
        self._config["screenshot_dir"] = str(path)
        self._save_config()
        logger.info(f"Screenshot directory set to: {path}")

    def get_all_settings(self) -> Dict[str, Any]:
        """
        获取所有配置设置

        Returns:
            包含所有配置的字典
        """
        return {
            "config_file": str(self.config_path),
            "driver_paths": {
                "chrome": self.get_chrome_driver_path(),
                "edge": self.get_edge_driver_path(),
            },
            "default_browser": self.get_default_browser(),
            "default_headless": self.get_default_headless(),
            "proxy": self.get_proxy(),
            "auto_fallback": self.get_auto_fallback_enabled(),
            "screenshot_dir": self.get_screenshot_dir(),
        }

    def reset_config(self) -> None:
        """重置配置为默认值"""
        self._config = {}
        self._save_config()


# 全局配置实例（单例模式）
_browser_config: Optional[BrowserConfig] = None


def get_browser_config() -> BrowserConfig:
    """
    获取全局浏览器配置实例（单例模式）

    Returns:
        BrowserConfig 实例
    """
    global _browser_config
    if _browser_config is None:
        _browser_config = BrowserConfig()
    return _browser_config
