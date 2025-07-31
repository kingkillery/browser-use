"""Configuration system for browser-use with automatic migration support."""

import json
import logging
import os
from datetime import datetime
from functools import cache
from pathlib import Path
from typing import Any
from uuid import uuid4

import psutil
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


@cache
def is_running_in_docker() -> bool:
	"""Detect if we are running in a docker container, for the purpose of optimizing chrome launch flags (dev shm usage, gpu settings, etc.)"""
	try:
		if Path('/.dockerenv').exists() or 'docker' in Path('/proc/1/cgroup').read_text().lower():
			return True
	except Exception:
		pass

	try:
		# if init proc (PID 1) looks like uvicorn/python/uv/etc. then we're in Docker
		# if init proc (PID 1) looks like bash/systemd/init/etc. then we're probably NOT in Docker
		init_cmd = ' '.join(psutil.Process(1).cmdline())
		if ('py' in init_cmd) or ('uv' in init_cmd) or ('app' in init_cmd):
			return True
	except Exception:
		pass

	try:
		# if less than 10 total running procs, then we're almost certainly in a container
		if len(psutil.pids()) < 10:
			return True
	except Exception:
		pass

	return False


class Config:
    """Configuration class for browser-use."""

    def __init__(self):
        # LLM configuration
        self.model = os.getenv("ANYLLM_MODEL", "openrouter/z-ai/glm-4.5-air:free")
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.temperature = float(os.getenv("ANYLLM_TEMPERATURE", 0.0))
        self.headless = os.getenv("BROWSER_USE_HEADLESS", "true").lower() in ("true", "1", "yes")
        
        # Docker detection
        self.IN_DOCKER = is_running_in_docker()
        
        # Directory configurations
        config_dir = Path.home() / '.config' / 'browseruse'
        self.BROWSER_USE_CONFIG_DIR = config_dir
        self.BROWSER_USE_DEFAULT_USER_DATA_DIR = config_dir / 'profiles' / 'default'
        self.BROWSER_USE_EXTENSIONS_DIR = config_dir / 'cache' / 'extensions'
        
        # Cloud sync configuration
        self.BROWSER_USE_CLOUD_SYNC = os.getenv("BROWSER_USE_CLOUD_SYNC", "false").lower() in ("true", "1", "yes")
        
        # LLM API key verification
        self.SKIP_LLM_API_KEY_VERIFICATION = os.getenv("SKIP_LLM_API_KEY_VERIFICATION", "false").lower() in ("true", "1", "yes")
    
    # Properties that read from environment variables dynamically
    @property
    def BROWSER_USE_LOGGING_LEVEL(self) -> str:
        return os.getenv('BROWSER_USE_LOGGING_LEVEL', 'info')
    
    @property
    def ANONYMIZED_TELEMETRY(self) -> bool:
        return os.getenv('ANONYMIZED_TELEMETRY', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def BROWSER_USE_CLOUD_API_URL(self) -> str:
        return os.getenv('BROWSER_USE_CLOUD_API_URL', 'https://api.browser-use.com')
    
    @property
    def BROWSER_USE_CLOUD_UI_URL(self) -> str:
        return os.getenv('BROWSER_USE_CLOUD_UI_URL', 'https://app.browser-use.com')
    
    @property
    def XDG_CACHE_HOME(self) -> Path:
        return Path(os.getenv('XDG_CACHE_HOME', Path.home() / '.cache'))
    
    @property
    def XDG_CONFIG_HOME(self) -> Path:
        return Path(os.getenv('XDG_CONFIG_HOME', Path.home() / '.config'))
    
    @property
    def BROWSER_USE_CONFIG_FILE(self) -> Path:
        return self.BROWSER_USE_CONFIG_DIR / 'config.json'
    
    @property
    def BROWSER_USE_PROFILES_DIR(self) -> Path:
        return self.BROWSER_USE_CONFIG_DIR / 'profiles'
    
    @property
    def OPENAI_API_KEY(self) -> str:
        return os.getenv('OPENAI_API_KEY', '')
    
    @property
    def ANTHROPIC_API_KEY(self) -> str:
        return os.getenv('ANTHROPIC_API_KEY', '')
    
    @property
    def GOOGLE_API_KEY(self) -> str:
        return os.getenv('GOOGLE_API_KEY', '')
    
    @property
    def DEEPSEEK_API_KEY(self) -> str:
        return os.getenv('DEEPSEEK_API_KEY', '')
    
    @property
    def GROK_API_KEY(self) -> str:
        return os.getenv('GROK_API_KEY', '')
    
    @property
    def NOVITA_API_KEY(self) -> str:
        return os.getenv('NOVITA_API_KEY', '')
    
    @property
    def AZURE_OPENAI_ENDPOINT(self) -> str:
        return os.getenv('AZURE_OPENAI_ENDPOINT', '')
    
    @property
    def AZURE_OPENAI_KEY(self) -> str:
        return os.getenv('AZURE_OPENAI_KEY', '')
    
    @property
    def IS_IN_EVALS(self) -> bool:
        return os.getenv('IS_IN_EVALS', 'false').lower() in ('true', '1', 'yes')
    
    @property
    def WIN_FONT_DIR(self) -> str:
        return os.getenv('WIN_FONT_DIR', 'C:/Windows/Fonts')

    def get_llm_config(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "api_key": self.api_key,
            "temperature": self.temperature,
        }

    def get_browser_config(self) -> dict[str, Any]:
        return {
            "headless": self.headless,
        }

CONFIG = Config()


def get_default_llm(config: dict) -> dict[str, Any]:
    """Get the default LLM configuration from config dict."""
    return config.get('llm', {})


def get_default_profile(config: dict) -> dict[str, Any]:
    """Get the default browser profile configuration from config dict."""
    return config.get('browser_profile', {})


def load_browser_use_config() -> dict[str, Any]:
    """Load browser-use configuration with environment variable overrides."""
    # Start with empty config
    config = {}
    
    # Load from config file if specified
    config_path = os.environ.get('BROWSER_USE_CONFIG_PATH')
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
    
    # Apply environment variable overrides
    llm_config = config.get('llm', {})
    if os.getenv('OPENAI_API_KEY'):
        llm_config['api_key'] = os.getenv('OPENAI_API_KEY')
    if os.getenv('BROWSER_USE_LLM_MODEL'):
        llm_config['model'] = os.getenv('BROWSER_USE_LLM_MODEL')
    config['llm'] = llm_config
    
    browser_config = config.get('browser_profile', {})
    if os.getenv('BROWSER_USE_HEADLESS'):
        browser_config['headless'] = os.getenv('BROWSER_USE_HEADLESS', 'false').lower() in ('true', '1', 'yes')
    config['browser_profile'] = browser_config
    
    return config
