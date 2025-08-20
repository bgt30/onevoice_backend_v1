import requests
import json
import os
from ai.utils import load_key

@except_handler("Failed to generate audio using 302.ai Fish TTS", retry=3, delay=1)
def fish_tts(text: str, save_as: str, workspace_path: str = ".", config_path: str = None) -> bool:
    """302.ai Fish TTS conversion"""
    API_KEY = load_key("fish_tts.api_key", config_path, workspace_path)
    character = load_key("fish_tts.character", config_path, workspace_path)
    refer_id = load_key("fish_tts.character_id_dict", config_path, workspace_path)[character]
    
    url = "https://api.302.ai/fish-audio/v1/tts"
    payload = json.dumps({
        "text": text,
        "reference_id": refer_id,
        "chunk_length": 200,
        "normalize": True,
        "format": "wav",
        "latency": "normal"
    })
    
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    response_data = response.json()
    
    if "url" in response_data:
        audio_response = requests.get(response_data["url"])
        audio_response.raise_for_status()
        
        # Save audio file with workspace_path
        audio_path = f"{workspace_path}/output/audio/segs/{save_as}"
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)
        return True
    
    print("Request failed:", response_data)
    return False

if __name__ == '__main__':
    fish_tts("Hi! Welcome to onevoice!", "test.wav")
