"""
Subagent 配置管理模块

提供安全的 API 密钥持久化存储和读取功能
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils import logger


class SubagentConfig:
    """Subagent 配置管理器"""

    DEFAULT_CONFIG_DIR = ".oh-my-mcp"
    DEFAULT_CONFIG_FILE = "subagent_config.json"

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
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
                self._config = {}
        else:
            logger.info(f"No config file found at {self.config_path}, using defaults")
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

            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_path}: {e}")
            raise

    def _migrate_old_config(self) -> None:
        """迁移旧的配置文件到新位置"""
        # 旧配置路径列表（按优先级）
        old_paths = [
            Path.home() / "oh-my-mcp" / self.DEFAULT_CONFIG_FILE,  # ~/oh-my-mcp/
            Path.home() / ".subagent_config.json",  # 最早的单文件配置
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
                    logger.info(f"Migrated config from {old_config_path} to {self.config_path}")
                    # 删除旧配置文件
                    old_config_path.unlink()
                    logger.info(f"Removed old config file: {old_config_path}")
                    return  # 迁移成功，退出循环
                except Exception as e:
                    logger.warning(f"Failed to migrate old config from {old_config_path}: {e}")

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        获取指定提供商的 API 密钥

        优先级：环境变量 > 配置文件

        Args:
            provider: 提供商名称 ("openai", "anthropic")

        Returns:
            API 密钥，如果未找到则返回 None
        """
        # 环境变量名映射
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }

        # 首先检查环境变量
        env_var = env_var_map.get(provider.lower())
        if env_var:
            env_value = os.getenv(env_var)
            if env_value:
                return env_value

        # 然后检查配置文件
        api_keys = self._config.get("api_keys", {})
        result: Optional[str] = api_keys.get(provider.lower())
        return result

    def get_enable_subagent(self) -> bool:
        """
        获取是否启用 Subagent 功能

        优先级：环境变量 > 配置文件 > 默认值(True)

        Returns:
            是否启用 Subagent，默认为 True
        """
        # 首先检查环境变量
        env_value = os.getenv("ENABLE_SUBAGENT")
        if env_value is not None:
            return env_value.lower() in ("true", "1", "yes", "on")

        # 然后检查配置文件
        config_value = self._config.get("enable_subagent")
        if config_value is not None:
            return bool(config_value)

        # 默认启用
        return True

    def set_enable_subagent(self, enabled: bool) -> None:
        """
        设置是否启用 Subagent 功能

        Args:
            enabled: 是否启用
        """
        self._config["enable_subagent"] = enabled
        self._save_config()
        logger.info(f"Set enable_subagent to {enabled}")

    def get_api_base(self, provider: str) -> Optional[str]:
        """
        获取指定提供商的 API 基础 URL

        优先级：环境变量 > 配置文件 > 默认值

        Args:
            provider: 提供商名称

        Returns:
            API 基础 URL
        """
        # 环境变量名映射
        env_var_map = {
            "openai": "OPENAI_API_BASE",
            "anthropic": "ANTHROPIC_API_BASE",
        }

        # 默认值
        defaults = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
        }

        # 首先检查环境变量
        env_var = env_var_map.get(provider.lower())
        if env_var:
            env_value = os.getenv(env_var)
            if env_value:
                return env_value

        # 然后检查配置文件
        api_bases = self._config.get("api_bases", {})
        config_value: Optional[str] = api_bases.get(provider.lower())
        if config_value:
            return config_value

        # 最后返回默认值
        return defaults.get(provider.lower())

    def set_api_key(self, provider: str, api_key: str) -> None:
        """
        设置指定提供商的 API 密钥

        Args:
            provider: 提供商名称
            api_key: API 密钥
        """
        if "api_keys" not in self._config:
            self._config["api_keys"] = {}

        self._config["api_keys"][provider.lower()] = api_key
        self._save_config()
        logger.info(f"Set API key for {provider}")

    def set_api_base(self, provider: str, api_base: str) -> None:
        """
        设置指定提供商的 API 基础 URL

        Args:
            provider: 提供商名称
            api_base: API 基础 URL
        """
        if "api_bases" not in self._config:
            self._config["api_bases"] = {}

        self._config["api_bases"][provider.lower()] = api_base
        self._save_config()
        logger.info(f"Set API base for {provider}")

    def remove_api_key(self, provider: str) -> None:
        """
        移除指定提供商的 API 密钥

        Args:
            provider: 提供商名称
        """
        if "api_keys" in self._config:
            self._config["api_keys"].pop(provider.lower(), None)
            self._save_config()
            logger.info(f"Removed API key for {provider}")

    def list_providers(self) -> Dict[str, Dict[str, str | None]]:
        """
        列出所有已配置的提供商

        Returns:
            提供商配置字典
        """
        result: Dict[str, Dict[str, str | None]] = {}

        for provider in ["openai", "anthropic"]:
            api_key = self.get_api_key(provider)
            api_base = self.get_api_base(provider)

            if api_key:
                # 脱敏显示密钥
                masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
                result[provider] = {
                    "api_key": masked_key,
                    "api_base": api_base,
                    "source": "env" if os.getenv(f"{provider.upper()}_API_KEY") else "config",
                }

        return result

    def export_config(self) -> str:
        """
        导出配置为 JSON 字符串

        Returns:
            配置的 JSON 表示
        """
        # 创建副本并脱敏
        export_config = self._config.copy()
        if "api_keys" in export_config:
            masked_keys = {}
            for provider, key in export_config["api_keys"].items():
                masked_keys[provider] = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            export_config["api_keys"] = masked_keys

        return json.dumps(export_config, indent=2, ensure_ascii=False)

    def get_config_path(self) -> str:
        """获取配置文件路径"""
        return str(self.config_path)


# 全局配置实例
_global_config: Optional[SubagentConfig] = None


def get_config() -> SubagentConfig:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = SubagentConfig()
    return _global_config


def init_config(config_path: Optional[str] = None) -> SubagentConfig:
    """
    初始化配置

    Args:
        config_path: 配置文件路径

    Returns:
        配置实例
    """
    global _global_config
    _global_config = SubagentConfig(config_path)
    return _global_config
