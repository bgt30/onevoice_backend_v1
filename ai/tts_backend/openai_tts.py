import requests
import json
import os
from ai.utils import load_key

def openai_tts(text, save_as, workspace_path: str = ".", config_path: str = None):
    """
    Generate TTS audio using OpenAI TTS API
    
    Args:
        text: Text to synthesize
        save_as: Output filename
        workspace_path: Path to workspace directory
        config_path: Path to config file
    """
    try:
        API_KEY = load_key("openai_tts.api_key", config_path, workspace_path)
        voice = load_key("openai_tts.voice", config_path, workspace_path)
        
        url = "https://api.openai.com/v1/audio/speech"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "tts-1",
            "input": text,
            "voice": voice,
            "response_format": "mp3",
            "speed": 1.0
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            # Save audio file
            audio_path = f"{workspace_path}/output/audio/segs/{save_as}"
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"OpenAI TTS API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"OpenAI TTS error: {str(e)}")
        return False

if __name__ == "__main__":
    # Test function
    result = openai_tts("Hello world", "test.wav")
    print(f"OpenAI TTS test result: {result}")