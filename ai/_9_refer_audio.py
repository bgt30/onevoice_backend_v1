import os
from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from ai.utils import *
from ai.utils.path_constants import get_8_1_audio_task, get_audio_refers_dir, get_audio_segs_dir, get_vocal_audio_file
import pandas as pd
import soundfile as sf

console = Console()
from ai.asr_backend.demucs_vl import demucs_audio

def time_to_samples(time_str, sr):
    """Unified time conversion function"""
    h, m, s = time_str.split(':')
    s, ms = s.split(',') if ',' in s else (s, '0')
    seconds = int(h) * 3600 + int(m) * 60 + float(s) + float(ms) / 1000
    return int(seconds * sr)

def extract_audio(audio_data, sr, start_time, end_time, out_file):
    """Simplified audio extraction function"""
    start = time_to_samples(start_time, sr)
    end = time_to_samples(end_time, sr)
    sf.write(out_file, audio_data[start:end], sr)

def extract_refer_audio_main(workspace_path: str = ".", config_path: str = None):
    """
    참조 오디오 추출
    
    Args:
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    demucs_audio(workspace_path, config_path) #!!! in case demucs not run
    
    audio_segs_dir = get_audio_segs_dir(workspace_path)
    if os.path.exists(os.path.join(audio_segs_dir, '1.wav')):
        rprint(Panel("Audio segments already exist, skipping extraction", title="Info", border_style="blue"))
        return

    # Create output directory
    audio_refers_dir = get_audio_refers_dir(workspace_path)
    os.makedirs(audio_refers_dir, exist_ok=True)
    
    # Read task file and audio data
    df = pd.read_excel(get_8_1_audio_task(workspace_path))
    vocal_audio_file = get_vocal_audio_file(workspace_path)
    data, sr = sf.read(vocal_audio_file)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Extracting audio segments...", total=len(df))
        
        for _, row in df.iterrows():
            out_file = os.path.join(audio_refers_dir, f"{row['number']}.wav")
            extract_audio(data, sr, row['start_time'], row['end_time'], out_file)
            progress.update(task, advance=1)
            
    rprint(Panel(f"Audio segments saved to {audio_refers_dir}", title="Success", border_style="green"))

if __name__ == "__main__":
    extract_refer_audio_main()