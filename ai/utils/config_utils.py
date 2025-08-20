from ruamel.yaml import YAML
import threading
import os

lock = threading.Lock()

yaml = YAML()
yaml.preserve_quotes = True

# -----------------------
# load & update config
# -----------------------

def load_key(key, config_path: str = None, workspace_path: str = None):
    """
    Load configuration value by key
    
    Args:
        key: Configuration key (e.g., 'whisper.language')
        config_path: Path to config file (optional, will use workspace config if not provided)
        workspace_path: Path to workspace directory (required if config_path not provided)
    """
    if config_path is None:
        if workspace_path is None:
            raise ValueError("Either config_path or workspace_path must be provided")
        # Use workspace-specific config path
        from ai.utils.workspace_utils import get_workspace_config_path
        config_path = get_workspace_config_path(workspace_path)
    
    with lock:
        with open(config_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file)

    keys = key.split('.')
    value = data
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            raise KeyError(f"Key '{k}' not found in configuration")
    return value

def update_key(key, new_value, config_path: str = None, workspace_path: str = None):
    """
    Update configuration value by key
    
    Args:
        key: Configuration key to update
        new_value: New value to set
        config_path: Path to config file (optional, will use workspace config if not provided)
        workspace_path: Path to workspace directory (required if config_path not provided)
    """
    if config_path is None:
        if workspace_path is None:
            raise ValueError("Either config_path or workspace_path must be provided")
        # Use workspace-specific config path
        from ai.utils.workspace_utils import get_workspace_config_path
        config_path = get_workspace_config_path(workspace_path)
        
    with lock:
        with open(config_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file)

        keys = key.split('.')
        current = data
        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return False

        if isinstance(current, dict) and keys[-1] in current:
            current[keys[-1]] = new_value
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file)
            return True
        else:
            raise KeyError(f"Key '{keys[-1]}' not found in configuration")
        
# basic utils
def get_joiner(language, config_path: str = None, workspace_path: str = None):
    """
    Get joiner character for language
    
    Args:
        language: Language code
        config_path: Path to config file (optional, will use workspace config if not provided)
        workspace_path: Path to workspace directory (required if config_path not provided)
    """
    if language in load_key('language_split_with_space', config_path, workspace_path):
        return " "
    elif language in load_key('language_split_without_space', config_path, workspace_path):
        return ""
    else:
        raise ValueError(f"Unsupported language code: {language}")

if __name__ == "__main__":
    # Test with workspace path
    test_workspace = "workspaces/test_job"
    print(load_key('language_split_with_space', workspace_path=test_workspace))
