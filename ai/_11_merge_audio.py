import os
import pandas as pd
import subprocess
from pydub import AudioSegment
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from ai.utils import *
from ai.utils.path_constants import get_8_1_audio_task, get_audio_segs_dir, get_output_dir

console = Console()

def load_and_flatten_data(excel_file):
    """Load and flatten Excel data"""
    df = pd.read_excel(excel_file)
    lines = [eval(line) if isinstance(line, str) else line for line in df['lines'].tolist()]
    lines = [item for sublist in lines for item in sublist]
    
    new_sub_times = [eval(time) if isinstance(time, str) else time for time in df['new_sub_times'].tolist()]
    new_sub_times = [item for sublist in new_sub_times for item in sublist]
    
    return df, lines, new_sub_times

def get_audio_files(df, workspace_path: str = "."):
    """Generate a list of audio file paths"""
    audios = []
    audio_segs_dir = get_audio_segs_dir(workspace_path)
    output_file_template = f"{audio_segs_dir}/{{}}.wav"
    
    for index, row in df.iterrows():
        number = row['number']
        line_count = len(eval(row['lines']) if isinstance(row['lines'], str) else row['lines'])
        for line_index in range(line_count):
            temp_file = output_file_template.format(f"{number}_{line_index}")
            audios.append(temp_file)
    return audios

def process_audio_segment(audio_file):
    """Process a single audio segment with MP3 compression"""
    temp_file = f"{audio_file}_temp.mp3"
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', audio_file,
        '-ar', '16000',
        '-ac', '1',
        '-b:a', '64k',
        temp_file
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    audio_segment = AudioSegment.from_mp3(temp_file)
    os.remove(temp_file)
    return audio_segment

def merge_audio_segments(audios, new_sub_times, sample_rate):
    merged_audio = AudioSegment.silent(duration=0, frame_rate=sample_rate)
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn()) as progress:
        merge_task = progress.add_task("🎵 Merging audio segments...", total=len(audios))
        
        for i, (audio_file, time_range) in enumerate(zip(audios, new_sub_times)):
            if not os.path.exists(audio_file):
                console.print(f"[bold yellow]⚠️  Warning: File {audio_file} does not exist, skipping...[/bold yellow]")
                progress.advance(merge_task)
                continue
                
            audio_segment = process_audio_segment(audio_file)
            start_time, end_time = time_range
            
            # Add silence segment
            if i > 0:
                prev_end = new_sub_times[i-1][1]
                silence_duration = start_time - prev_end
                if silence_duration > 0:
                    silence = AudioSegment.silent(duration=int(silence_duration * 1000), frame_rate=sample_rate)
                    merged_audio += silence
            elif start_time > 0:
                silence = AudioSegment.silent(duration=int(start_time * 1000), frame_rate=sample_rate)
                merged_audio += silence
                
            merged_audio += audio_segment
            progress.advance(merge_task)
    
    return merged_audio

def create_srt_subtitle(workspace_path: str = ".", config_path: str = None):
    excel_file = get_8_1_audio_task(workspace_path)
    df, lines, new_sub_times = load_and_flatten_data(excel_file)
    
    output_dir = get_output_dir(workspace_path)
    dub_sub_file = f"{output_dir}/dub.srt"
    
    with open(dub_sub_file, 'w', encoding='utf-8') as f:
        for i, ((start_time, end_time), line) in enumerate(zip(new_sub_times, lines), 1):
            start_str = f"{int(start_time//3600):02d}:{int((start_time%3600)//60):02d}:{int(start_time%60):02d},{int((start_time*1000)%1000):03d}"
            end_str = f"{int(end_time//3600):02d}:{int((end_time%3600)//60):02d}:{int(end_time%60):02d},{int((end_time*1000)%1000):03d}"
            
            f.write(f"{i}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{line}\n\n")
    
    rprint(f"[bold green]✅ Subtitle file created: {dub_sub_file}[/bold green]")

def merge_full_audio(workspace_path: str = ".", config_path: str = None):
    """
    오디오 병합
    
    Args:
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    console.print("\n[bold cyan]🎬 Starting audio merging process...[/bold cyan]")
    
    excel_file = get_8_1_audio_task(workspace_path)
    with console.status("[bold cyan]📊 Loading data from Excel...[/bold cyan]"):
        df, lines, new_sub_times = load_and_flatten_data(excel_file)
    console.print("[bold green]✅ Data loaded successfully[/bold green]")
    
    with console.status("[bold cyan]🔍 Getting audio file list...[/bold cyan]"):
        audios = get_audio_files(df, workspace_path)
    console.print(f"[bold green]✅ Found {len(audios)} audio segments[/bold green]")
    
    with console.status("[bold cyan]📝 Generating subtitle file...[/bold cyan]"):
        create_srt_subtitle(workspace_path, config_path)
    
    if not os.path.exists(audios[0]):
        console.print(f"[bold red]❌ Error: First audio file {audios[0]} does not exist![/bold red]")
        return
    
    sample_rate = 16000
    console.print(f"[bold green]✅ Sample rate: {sample_rate}Hz[/bold green]")

    console.print("[bold cyan]🔄 Starting audio merge process...[/bold cyan]")
    merged_audio = merge_audio_segments(audios, new_sub_times, sample_rate)
    
    output_dir = get_output_dir(workspace_path)
    dub_vocal_file = f"{output_dir}/dub.mp3"
    
    with console.status("[bold cyan]💾 Exporting final audio file...[/bold cyan]"):
        merged_audio = merged_audio.set_frame_rate(16000).set_channels(1)
        merged_audio.export(dub_vocal_file, format="mp3", parameters=["-b:a", "64k"])
    console.print(f"[bold green]✅ Audio file successfully merged![/bold green]")
    console.print(f"[bold green]📁 Output file: {dub_vocal_file}[/bold green]")

if __name__ == "__main__":
    merge_full_audio()