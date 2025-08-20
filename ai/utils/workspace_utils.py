"""
Workspace utilities for AI modules

This module provides utilities for AI modules to work with workspace paths
without depending on os.chdir() or hardcoded paths.
"""

import os
from typing import Optional
from pathlib import Path
from ai.utils import load_key

class WorkspaceContext:
    """
    Context manager for workspace operations
    
    This allows AI modules to work with a specific workspace
    without changing the global working directory.
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.original_cwd = None
        
    def __enter__(self):
        self.original_cwd = os.getcwd()
        os.chdir(self.workspace_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_cwd:
            os.chdir(self.original_cwd)

def ensure_workspace_dirs(workspace_path: str) -> None:
    """
    Ensure all required directories exist in workspace
    
    Args:
        workspace_path: Path to workspace directory
    """
    dirs = [
        f"{workspace_path}/output",
        f"{workspace_path}/output/log", 
        f"{workspace_path}/output/audio",
        f"{workspace_path}/output/audio/refers",
        f"{workspace_path}/output/audio/segs",
        f"{workspace_path}/output/audio/tmp"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def get_workspace_config_path(workspace_path: str, config_name: str = "config.yaml") -> str:
    """
    Get config file path in workspace
    
    Args:
        workspace_path: Path to workspace directory
        config_name: Name of config file (default: config.yaml)
        
    Returns:
        Full path to config file in workspace
    """
    return f"{workspace_path}/{config_name}"

def get_workspace_custom_terms_path(workspace_path: str, terms_name: str = "custom_terms.xlsx") -> str:
    """
    Get custom terms file path in workspace
    
    Args:
        workspace_path: Path to workspace directory
        terms_name: Name of terms file (default: custom_terms.xlsx)
        
    Returns:
        Full path to terms file in workspace
    """
    return f"{workspace_path}/{terms_name}"

def find_video_in_workspace(workspace_path: str, config_path: str = None) -> Optional[str]:
    """
    Find video file in workspace output directory
    
    Args:
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
        
    Returns:
        Path to video file if found, None otherwise
    """
    output_dir = f"{workspace_path}/output"
    if not os.path.exists(output_dir):
        return None
        
    # Use allowed video formats from config
    video_extensions = load_key("allowed_video_formats", config_path, workspace_path)
    
    for file in os.listdir(output_dir):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            return f"{output_dir}/{file}"
            
    return None

def get_workspace_file_path(workspace_path: str, relative_path: str) -> str:
    """
    Get absolute path for a file relative to workspace
    
    Args:
        workspace_path: Path to workspace directory
        relative_path: Path relative to workspace (e.g., "output/log/file.txt")
        
    Returns:
        Absolute path to file
    """
    return f"{workspace_path}/{relative_path}"

def workspace_exists(workspace_path: str) -> bool:
    """
    Check if workspace directory exists
    
    Args:
        workspace_path: Path to workspace directory
        
    Returns:
        True if workspace exists, False otherwise
    """
    return os.path.exists(workspace_path) and os.path.isdir(workspace_path) 