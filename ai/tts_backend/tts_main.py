import os
import re
from pydub import AudioSegment

from ai.asr_backend.audio_preprocess import get_audio_duration
from ai.tts_backend.openai_tts import openai_tts
from ai.tts_backend.fish_tts import fish_tts
from ai.tts_backend.custom_tts import custom_tts
from ai.prompts import get_correct_text_prompt
from ai.tts_backend._302_f5tts import f5_tts_for_onevoice
from ai.utils import *

def clean_text_for_tts(text):
    """Remove problematic characters for TTS"""
    chars_to_remove = ['&', '®', '™', '©']
    for char in chars_to_remove:
        text = text.replace(char, '')
    return text.strip()

def tts_main(text, save_as, number, task_df, workspace_path: str = ".", config_path: str = None):
    """
    TTS 메인 함수
    
    Args:
        text: Text to convert to speech
        save_as: Output file path
        number: Task number
        task_df: Task dataframe
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    text = clean_text_for_tts(text)
    # Check if text is empty or single character, single character voiceovers are prone to bugs
    cleaned_text = re.sub(r'[^\w\s]', '', text).strip()
    if not cleaned_text or len(cleaned_text) <= 1:
        silence = AudioSegment.silent(duration=100)  # 100ms = 0.1s
        silence.export(save_as, format="wav")
        rprint(f"Created silent audio for empty/single-char text: {save_as}")
        return
    
    # Skip if file exists
    if os.path.exists(save_as):
        return
    
    print(f"Generating <{text}...>")
    tts_method = load_key("tts_method", config_path)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt >= max_retries - 1:
                print("Asking GPT to correct text...")
                correct_text = ask_gpt(get_correct_text_prompt(text), resp_type="json", log_title='tts_correct_text')
                text = correct_text['text']
            if tts_method == 'openai_tts':
                openai_tts(text, save_as, workspace_path, config_path)
            elif tts_method == 'fish_tts':
                fish_tts(text, save_as, workspace_path, config_path)
            elif tts_method == 'custom_tts':
                custom_tts(text, save_as, workspace_path, config_path)
            elif tts_method == 'f5tts':
                f5_tts_for_onevoice(text, save_as, number, task_df, workspace_path, config_path)
                
            # Check generated audio duration
            duration = get_audio_duration(save_as)
            if duration > 0:
                break
            else:
                if os.path.exists(save_as):
                    os.remove(save_as)
                if attempt == max_retries - 1:
                    print(f"Warning: Generated audio duration is 0 for text: {text}")
                    # Create silent audio file
                    silence = AudioSegment.silent(duration=100)  # 100ms silence
                    silence.export(save_as, format="wav")
                    return
                print(f"Attempt {attempt + 1} failed, retrying...")
        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(f"Failed to generate audio after {max_retries} attempts: {str(e)}")
            print(f"Attempt {attempt + 1} failed, retrying...")