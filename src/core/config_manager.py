"""
Configuration Manager - Secure API key and settings management.

Manages environment variables, API keys, and application configuration.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, Dict, Any
import os
from pathlib import Path
import yaml
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages application configuration and secrets.
    
    Loads configuration from:
    - Environment variables
    - .env file
    - config.yaml file
    - Default values
    """
    
    def __init__(self, env_file: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            env_file: Path to .env file (default: .env in project root)
            config_file: Path to config.yaml (default: config/config.yaml)
        """
        # Load .env file
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from default .env
        
        # Load YAML config
        self.config_data = {}
        if config_file:
            self.config_data = self._load_yaml_config(config_file)
        elif Path("config/config.yaml").exists():
            self.config_data = self._load_yaml_config("config/config.yaml")
    
    def _load_yaml_config(self, path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            return {}
    
    # API Keys
    def get_anthropic_key(self) -> Optional[str]:
        """Get Anthropic (Claude) API key."""
        return os.getenv('ANTHROPIC_API_KEY')
    
    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key."""
        return os.getenv('OPENAI_API_KEY')
    
    def get_tmdb_key(self) -> Optional[str]:
        """Get TMDB API key."""
        return os.getenv('TMDB_API_KEY')
    
    # Database Configuration
    def get_postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return os.getenv(
            'POSTGRES_URL',
            'postgresql://user:password@localhost:5432/doppelganger'
        )
    
    def get_mongodb_url(self) -> str:
        """Get MongoDB connection URL."""
        return os.getenv(
            'MONGODB_URL',
            'mongodb://localhost:27017/doppelganger'
        )
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL."""
        return os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Application Settings
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Config key (dot notation supported, e.g., 'ai.temperature')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # Try environment variable first
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Try YAML config
        keys = key.split('.')
        value = self.config_data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value if value != self.config_data else default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on')
        return default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value."""
        value = self.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default


# Global config instance
_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config


def init_config(env_file: Optional[str] = None, config_file: Optional[str] = None):
    """Initialize global configuration."""
    global _config
    _config = ConfigManager(env_file, config_file)
