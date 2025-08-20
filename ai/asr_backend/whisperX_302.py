import os
import io
import json
import time
import requests
import librosa
import soundfile as sf
from rich import print as rprint
from ai.utils import *

def transcribe_audio_302(raw_audio_path: str, vocal_audio_path: str, start: float = None, end: float = None, workspace_path: str = ".", config_path: str = None):
    """
    302.ai WhisperX API를 사용한 음성 인식
    
    Args:
        raw_audio_path: Path to raw audio file
        vocal_audio_path: Path to vocal audio file
        start: Start time in seconds
        end: End time in seconds
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    output_log_dir = f"{workspace_path}/output/log"
    os.makedirs(output_log_dir, exist_ok=True)
    log_file = f"{output_log_dir}/whisperx302_{start}_{end}.json"
    
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            return json.load(f)
        
    whisper_language = load_key("whisper.language", config_path)
    update_key("whisper.language", whisper_language, config_path)
    url = "https://api.302.ai/302/whisperx"
    
    y, sr = librosa.load(vocal_audio_path, sr=16000)
    audio_duration = len(y) / sr
    
    if start is None or end is None:
        start = 0
        end = audio_duration
        
    start_sample = int(start * sr)
    end_sample = int(end * sr)
    y_slice = y[start_sample:end_sample]
    
    audio_buffer = io.BytesIO()
    sf.write(audio_buffer, y_slice, sr, format='WAV', subtype='PCM_16')
    audio_buffer.seek(0)
    
    files = [('audio_input', ('audio_slice.wav', audio_buffer, 'application/octet-stream'))]
    payload = {"processing_type": "align", "language": whisper_language, "output": "raw"}
    
    start_time = time.time()
    rprint(f"[cyan]🎤 Transcribing audio with language:  <{whisper_language}> ...[/cyan]")
    headers = {'Authorization': f'Bearer {load_key("whisper.whisperX_302_api_key", config_path)}'}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    
    response_json = response.json()
    
    if start is not None:
        for segment in response_json['segments']:
            segment['start'] += start
            segment['end'] += start
            for word in segment.get('words', []):
                if 'start' in word:
                    word['start'] += start
                if 'end' in word:
                    word['end'] += start
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(response_json, f, indent=4, ensure_ascii=False)
    
    elapsed_time = time.time() - start_time
    rprint(f"[green]✓ Transcription completed in {elapsed_time:.2f} seconds[/green]")
    return response_json

if __name__ == "__main__":  
    result = transcribe_audio_302("raw_audio.mp3", "raw_audio.mp3")
    rprint(result)
