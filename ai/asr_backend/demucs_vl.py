import os
import torch
from rich.console import Console
from rich import print as rprint
from demucs.pretrained import get_model
from demucs.audio import save_audio
from torch.cuda import is_available as is_cuda_available
from typing import Optional
from demucs.api import Separator
from demucs.apply import BagOfModels
import gc
from ai.utils.path_constants import get_audio_dir, get_raw_audio_file, get_vocal_audio_file, get_background_audio_file

class PreloadedSeparator(Separator):
    def __init__(self, model: BagOfModels, shifts: int = 1, overlap: float = 0.25,
                 split: bool = True, segment: Optional[int] = None, jobs: int = 0):
        self._model, self._audio_channels, self._samplerate = model, model.audio_channels, model.samplerate
        device = "cuda" if is_cuda_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.update_parameter(device=device, shifts=shifts, overlap=overlap, split=split,
                            segment=segment, jobs=jobs, progress=True, callback=None, callback_arg=None)

def demucs_audio(workspace_path: str = ".", config_path: str = None):
    """
    Demucs를 사용한 오디오 분리
    
    Args:
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    audio_dir = get_audio_dir(workspace_path)
    raw_audio_file = get_raw_audio_file(workspace_path)
    vocal_audio_file = get_vocal_audio_file(workspace_path)
    background_audio_file = get_background_audio_file(workspace_path)
    
    if os.path.exists(vocal_audio_file) and os.path.exists(background_audio_file):
        rprint(f"[yellow]⚠️ {vocal_audio_file} and {background_audio_file} already exist, skip Demucs processing.[/yellow]")
        return
    
    console = Console()
    os.makedirs(audio_dir, exist_ok=True)
    
    console.print("🤖 Loading <htdemucs> model...")
    model = get_model('htdemucs')
    separator = PreloadedSeparator(model=model, shifts=1, overlap=0.25)
    
    console.print("🎵 Separating audio...")
    _, outputs = separator.separate_audio_file(raw_audio_file)
    
    kwargs = {"samplerate": model.samplerate, "bitrate": 128, "preset": 2, 
             "clip": "rescale", "as_float": False, "bits_per_sample": 16}
    
    console.print("🎤 Saving vocals track...")
    save_audio(outputs['vocals'].cpu(), vocal_audio_file, **kwargs)
    
    console.print("🎹 Saving background music...")
    background = sum(audio for source, audio in outputs.items() if source != 'vocals')
    save_audio(background.cpu(), background_audio_file, **kwargs)
    
    # Clean up memory
    del outputs, background, model, separator
    gc.collect()
    
    console.print("[green]✨ Audio separation completed![/green]")

if __name__ == "__main__":
    demucs_audio()
