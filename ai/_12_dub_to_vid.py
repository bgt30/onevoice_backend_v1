import platform
import subprocess

import cv2
import numpy as np
from rich.console import Console

from ai._1_find_video import find_video_files
from ai.asr_backend.audio_preprocess import normalize_audio_volume
from ai.utils import *
from ai.utils.path_constants import get_output_dir, get_background_audio_file

console = Console()

TRANS_FONT_SIZE = 17
TRANS_FONT_NAME = 'Arial'
if platform.system() == 'Linux':
    TRANS_FONT_NAME = 'NotoSansCJK-Regular'
if platform.system() == 'Darwin':
    TRANS_FONT_NAME = 'Arial Unicode MS'

TRANS_FONT_COLOR = '&H00FFFF'
TRANS_OUTLINE_COLOR = '&H000000'
TRANS_OUTLINE_WIDTH = 1 
TRANS_BACK_COLOR = '&H33000000'

def merge_video_audio(workspace_path: str = ".", config_path: str = None):
    """
    비디오와 오디오 병합
    
    Args:
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    output_dir = get_output_dir(workspace_path)
    dub_video = f"{output_dir}/output_dub.mp4"
    dub_sub_file = f"{output_dir}/dub.srt"
    dub_audio = f"{output_dir}/dub.mp3"
    
    VIDEO_FILE = find_video_files(workspace_path, config_path)
    background_file = get_background_audio_file(workspace_path)
    
    if not load_key("burn_subtitles", config_path):
        rprint("[bold yellow]Warning: A 0-second black video will be generated as a placeholder as subtitles are not burned in.[/bold yellow]")

        # Create a black frame
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(dub_video, fourcc, 1, (1920, 1080))
        out.write(frame)
        out.release()

        rprint("[bold green]Placeholder video has been generated.[/bold green]")
        return

    # Normalize dub audio
    normalized_dub_audio = f"{output_dir}/normalized_dub.wav"
    normalize_audio_volume(dub_audio, normalized_dub_audio)
    
    # Merge video and audio with translated subtitles
    video = cv2.VideoCapture(VIDEO_FILE)
    TARGET_WIDTH = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    TARGET_HEIGHT = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video.release()
    rprint(f"[bold green]Video resolution: {TARGET_WIDTH}x{TARGET_HEIGHT}[/bold green]")
    
    subtitle_filter = (
        f"subtitles={dub_sub_file}:force_style='FontSize={TRANS_FONT_SIZE},"
        f"FontName={TRANS_FONT_NAME},PrimaryColour={TRANS_FONT_COLOR},"
        f"OutlineColour={TRANS_OUTLINE_COLOR},OutlineWidth={TRANS_OUTLINE_WIDTH},"
        f"BackColour={TRANS_BACK_COLOR},Alignment=2,MarginV=27,BorderStyle=4'"
    )
    
    cmd = [
        'ffmpeg', '-y', '-i', VIDEO_FILE, '-i', background_file, '-i', normalized_dub_audio,
        '-filter_complex',
        f'[0:v]scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,'
        f'pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,'
        f'{subtitle_filter}[v];'
        f'[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=3[a]'
    ]

    if load_key("ffmpeg_gpu", config_path):
        rprint("[bold green]Using GPU acceleration...[/bold green]")
        cmd.extend(['-map', '[v]', '-map', '[a]', '-c:v', 'h264_nvenc'])
    else:
        cmd.extend(['-map', '[v]', '-map', '[a]'])
    
    cmd.extend(['-c:a', 'aac', '-b:a', '96k', dub_video])
    
    subprocess.run(cmd)
    rprint(f"[bold green]Video and audio successfully merged into {dub_video}[/bold green]")

if __name__ == '__main__':
    merge_video_audio()
