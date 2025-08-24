from ai.utils import *
from ai.asr_backend.demucs_vl import demucs_audio
from ai.asr_backend.audio_preprocess import process_transcription, convert_video_to_audio, split_audio, save_results, normalize_audio_volume
from ai._1_find_video import find_video_files
from ai.utils.path_constants import get_2_cleaned_chunks, get_raw_audio_file, get_vocal_audio_file
import os

def transcribe(workspace_path: str = ".", config_path: str = None):
    """
    음성 인식 및 전사
    
    Args:
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    output_file = get_2_cleaned_chunks(workspace_path)
    
    # Check if output file already exists
    if os.path.exists(output_file):
        print(f"Output file already exists: {output_file}")
        return
    
    # 1. video to audio
    video_file = find_video_files(workspace_path, config_path)
    convert_video_to_audio(video_file, workspace_path, config_path)

    # 2. Demucs vocal separation:
    if load_key("demucs", config_path):
        demucs_audio(workspace_path, config_path)
        vocal_audio = normalize_audio_volume(
            get_vocal_audio_file(workspace_path), 
            get_vocal_audio_file(workspace_path), 
            format="mp3"
        )
    else:
        vocal_audio = get_raw_audio_file(workspace_path)

    # 3. Extract audio
    segments = split_audio(get_raw_audio_file(workspace_path))
    
    # 4. Transcribe audio by clips
    all_results = []
    runtime = load_key("whisper.runtime", config_path)
    if runtime == "cloud":
        from ai.asr_backend.whisperX_302 import transcribe_audio_302 as ts
        rprint("[cyan]🎤 Transcribing audio with 302 API...[/cyan]")
    elif runtime == "elevenlabs":
        from ai.asr_backend.elevenlabs_asr import transcribe_audio_elevenlabs as ts
        rprint("[cyan]🎤 Transcribing audio with ElevenLabs API...[/cyan]")
    elif runtime == "openai":
        from ai.asr_backend.openai_asr import transcribe_audio_openai as ts
        rprint("[cyan]🎤 Transcribing audio with OpenAI API...[/cyan]")
    else:
        raise ValueError(f"Unsupported runtime: {runtime}. Supported options: cloud, elevenlabs, openai")

    for start, end in segments:
        result = ts(get_raw_audio_file(workspace_path), vocal_audio, start, end)
        all_results.append(result)
    
    # 5. Combine results
    combined_result = {'segments': []}
    for result in all_results:
        combined_result['segments'].extend(result['segments'])
    
    # 6. Process df
    df = process_transcription(combined_result)
    save_results(df, workspace_path, config_path)
        
if __name__ == "__main__":
    transcribe()