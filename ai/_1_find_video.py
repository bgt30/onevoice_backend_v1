import os
import sys
from ai.utils.workspace_utils import find_video_in_workspace

def find_video_files(workspace_path: str, config_path: str = None) -> str:
    """workspace의 output 폴더에서 비디오 파일을 찾는 함수"""
    video_file = find_video_in_workspace(workspace_path, config_path)
    
    if video_file is None:
        raise ValueError("No video file found in workspace output directory.")
    
    # Windows 경로 정규화 (\\를 /로 변경)
    if sys.platform.startswith('win'):
        video_file = video_file.replace("\\", "/")
    
    return video_file