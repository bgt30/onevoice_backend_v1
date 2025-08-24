import os
import io
import json
import time
import librosa
import soundfile as sf
import requests
from typing import Dict, List
from rich import print as rprint
from ai.utils.config_utils import load_key


def transcribe_audio_openai(raw_audio_path: str, vocal_audio_path: str, start: float = None, end: float = None, workspace_path: str = ".", config_path: str = None) -> Dict:
    """
    Transcribe audio using OpenAI Audio Transcriptions API with required parameters:
    - model="whisper-1"
    - response_format="verbose_json"
    - timestamp_granularities=["segment", "word"]

    Returns a whisper-like structure with segments and a single word entry per segment
    to satisfy downstream expectations without per-token timing computation.
    """
    os.makedirs(f"{workspace_path}/output/log", exist_ok=True)
    log_file = f"{workspace_path}/output/log/openai_transcribe_{start}_{end}.json"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            return json.load(f)

    language = load_key("whisper.language", config_path, workspace_path)
    api_key = load_key("whisper.openai_api_key", config_path, workspace_path)

    # Prepare audio slice
    y, sr = librosa.load(vocal_audio_path, sr=16000)
    total_duration = len(y) / sr if sr else 0.0
    s = 0.0 if start is None else max(0.0, float(start))
    e = total_duration if end is None else min(float(end), total_duration)
    s_i, e_i = int(s * sr), int(e * sr)
    y_slice = y[s_i:e_i]

    audio_buffer = io.BytesIO()
    sf.write(audio_buffer, y_slice, sr, format='WAV', subtype='PCM_16')
    audio_buffer.seek(0)

    url = "https://api.openai.com/v1/audio/transcriptions"
    files = {"file": ("audio_slice.wav", audio_buffer, "audio/wav")}
    # Use multipart form fields; list values are sent as repeated keys with [] suffix
    data = [
        ("model", "whisper-1"),
        ("response_format", "verbose_json"),
        ("timestamp_granularities[]", "segment"),
        ("timestamp_granularities[]", "word"),
        ("language", language),
    ]
    headers = {"Authorization": f"Bearer {api_key}"}

    start_time = time.time()
    rprint("[cyan]🎤 Transcribing audio with OpenAI model: <whisper-1>...[/cyan]")
    response = requests.post(url, headers=headers, data=data, files=files)

    try:
        response.raise_for_status()
        body = response.json()
    except Exception as e:
        try:
            err_body = response.json()
        except Exception:
            err_body = {"error": response.text}
        raise RuntimeError(f"OpenAI transcription failed: {err_body}") from e

    # Normalize to whisper-like format without synthesizing words unless missing
    segments_in: List[Dict] = body.get("segments", []) if isinstance(body, dict) else []
    segments_out: List[Dict] = []
    for seg in segments_in:
        seg_start = float(seg.get("start", 0.0)) + s
        seg_end = float(seg.get("end", seg_start)) + s
        text = (seg.get("text") or "").strip()

        # Offset-correct words if present; otherwise, create a minimal one-item words list
        words_in = seg.get("words") or []
        if words_in:
            words_out = []
            for w in words_in:
                w_text = (w.get("word") or w.get("text") or "").strip()
                w_start = float(w.get("start", 0.0)) + s if "start" in w else seg_start
                w_end = float(w.get("end", w_start)) + s if "end" in w else seg_end
                words_out.append({"word": w_text, "start": w_start, "end": w_end})
        else:
            words_out = [{"word": text, "start": seg_start, "end": seg_end}]

        segments_out.append({
            "text": text,
            "start": seg_start,
            "end": seg_end,
            "speaker_id": None,
            "words": words_out,
        })

    result = {"segments": segments_out}

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    rprint(f"[green]✓ Transcription completed in {time.time() - start_time:.2f} seconds[/green]")
    return result


if __name__ == "__main__":
    test_file = input("Enter path to audio file: ").strip()
    out = transcribe_audio_openai(test_file, test_file, 0, None)
    print(json.dumps(out, ensure_ascii=False)[:500])


