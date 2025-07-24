import yaml
import os
from collections import OrderedDict
from pathlib import Path


class ConfigError(Exception):
    """Custom exception for configuration-related errors"""
    pass


class DictToObj:
    """Convert dictionary to object with attribute access"""

    def __init__(self, dictionary):
        if not isinstance(dictionary, dict):
            raise TypeError(f"Expected dict, got {type(dictionary).__name__}")

        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, DictToObj(value))
            elif isinstance(value, list):
                # Handle lists that might contain dictionaries
                setattr(self, key, [DictToObj(item) if isinstance(item, dict) else item for item in value])
            else:
                setattr(self, key, value)

    def __getitem__(self, key):
        """Allow both dict-style and object-style access for backward compatibility"""
        return getattr(self, key)

    def __setitem__(self, key, value):
        """Allow dict-style assignment"""
        setattr(self, key, value)

    def __getattr__(self, key):
        """Handle missing attributes with a clear error message"""
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def get(self, key, default=None):
        """Provide dict-like get method"""
        return getattr(self, key, default)

    def __contains__(self, key):
        """Support 'in' operator"""
        return hasattr(self, key)

    def __repr__(self):
        """Return a string representation that could recreate the object"""
        try:
            return f"DictToObj({self._to_dict()})"
        except Exception as e:
            return f"<DictToObj - repr error: {e}>"

    def __str__(self):
        """Return a human-readable string representation"""
        try:
            import json
            return json.dumps(self._to_dict(), indent=2, sort_keys=True, default=str)
        except Exception as e:
            return f"<DictToObj - serialization error: {e}>"

    def _to_dict(self, _seen=None, _max_depth=100, _current_depth=0):
        """Convert the object back to a dictionary with circular reference protection"""
        if _seen is None:
            _seen = set()

        if _current_depth > _max_depth:
            return "<Max depth exceeded>"

        obj_id = id(self)
        if obj_id in _seen:
            return "<Circular reference>"

        _seen.add(obj_id)
        result = {}

        try:
            # Use __dict__ instead of dir() to avoid methods and only get actual attributes
            for key, value in self.__dict__.items():
                if isinstance(value, DictToObj):
                    result[key] = value._to_dict(_seen.copy(), _max_depth, _current_depth + 1)
                elif isinstance(value, list):
                    result[key] = [
                        item._to_dict(_seen.copy(), _max_depth, _current_depth + 1)
                        if isinstance(item, DictToObj) else item
                        for item in value
                    ]
                else:
                    result[key] = value
        except Exception as e:
            result['_error'] = f"Error processing attributes: {e}"
        finally:
            _seen.discard(obj_id)  # Use discard to avoid KeyError if already removed

        return result


def _deep_merge(base_dict, override_dict):
    """
    Deep merge two dictionaries.
    Values in override_dict take precedence over base_dict.

    Args:
        base_dict: The base dictionary
        override_dict: The dictionary whose values override the base

    Returns:
        Merged dictionary
    """
    if not isinstance(base_dict, dict) or not isinstance(override_dict, dict):
        return override_dict

    result = base_dict.copy()

    for key, value in override_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        elif key in result and isinstance(result[key], list) and isinstance(value, list):
            # For lists, we can either extend or replace - let's replace for simplicity
            # This behavior can be made configurable in the future
            result[key] = value
        else:
            result[key] = value

    return result


def _resolve_config_path(config_path, base_dir):
    """
    Resolve a config path relative to base_dir.

    Args:
        config_path: Path to the config file (relative or absolute)
        base_dir: Base directory for relative paths

    Returns:
        Absolute path to the config file
    """
    if os.path.isabs(config_path):
        return config_path
    return os.path.join(base_dir, config_path)


def _load_config_file(config_path, visited_files=None, base_dir=None):
    """
    Load a single config file and process its extends.

    Args:
        config_path: Path to the config file
        visited_files: Set of already visited files (for circular dependency detection)
        base_dir: Base directory for resolving relative paths

    Returns:
        Merged configuration dictionary
    """
    if visited_files is None:
        visited_files = set()

    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(config_path))

    # Resolve absolute path for circular dependency detection
    abs_config_path = os.path.abspath(config_path)

    if abs_config_path in visited_files:
        raise ConfigError(f"Circular dependency detected: {abs_config_path}")

    if not os.path.exists(config_path):
        raise ConfigError(f"Config file not found: {config_path}")

    visited_files.add(abs_config_path)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {config_path}: {e}")
    except Exception as e:
        raise ConfigError(f"Error reading {config_path}: {e}")

    # Check if this config extends other configs
    extends = config_dict.pop("extends", None)

    if extends is None:
        visited_files.remove(abs_config_path)
        return config_dict

    if not isinstance(extends, list):
        raise ConfigError(f"'extends' must be a list in {config_path}, got {type(extends).__name__}")

    # Start with an empty base config
    merged_config = {}

    # Process extended configs in order
    for extend_path in extends:
        if not isinstance(extend_path, str):
            raise ConfigError(f"All paths in 'extends' must be strings in {config_path}, got {type(extend_path).__name__}")

        resolved_path = _resolve_config_path(extend_path, base_dir)
        extended_config = _load_config_file(resolved_path, visited_files, base_dir)
        merged_config = _deep_merge(merged_config, extended_config)

    # Merge the current config on top of extended configs
    final_config = _deep_merge(merged_config, config_dict)

    visited_files.remove(abs_config_path)
    return final_config


def load_config():
    config_path = os.path.join(os.getcwd(), "config.yaml")

    try:
        config_dict = _load_config_file(config_path)
        return DictToObj(config_dict)
    except ConfigError:
        raise
    except Exception as e:
        raise ConfigError(f"Unexpected error loading config: {e}")
