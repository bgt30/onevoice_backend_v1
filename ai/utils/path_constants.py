# ------------------------------------------
# Defining intermediate output files
# ------------------------------------------

def get_2_cleaned_chunks(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/log/cleaned_chunks.xlsx"

def get_3_1_split_by_nlp(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/log/split_by_nlp.txt"

def get_3_2_split_by_meaning(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/log/split_by_meaning.txt"

def get_4_1_terminology(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/log/terminology.json"

def get_4_2_translation(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/log/translation_results.xlsx"

def get_5_split_sub(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/log/translation_results_for_subtitles.xlsx"

def get_5_remerged(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/log/translation_results_remerged.xlsx"

def get_8_1_audio_task(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/audio/tts_tasks.xlsx"

# ------------------------------------------
# Define audio file
# ------------------------------------------
def get_output_dir(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output"

def get_audio_dir(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/audio"

def get_raw_audio_file(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/audio/raw.mp3"

def get_vocal_audio_file(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/audio/vocal.mp3"

def get_background_audio_file(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/audio/background.mp3"

def get_audio_refers_dir(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/audio/refers"

def get_audio_segs_dir(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/audio/segs"

def get_audio_tmp_dir(workspace_path: str = ".") -> str:
    return f"{workspace_path}/output/audio/tmp"

# ------------------------------------------
# Export
# ------------------------------------------

__all__ = [
    # New functions
    "get_2_cleaned_chunks",
    "get_3_1_split_by_nlp", 
    "get_3_2_split_by_meaning",
    "get_4_1_terminology",
    "get_4_2_translation",
    "get_5_split_sub",
    "get_5_remerged",
    "get_8_1_audio_task",
    "get_output_dir",
    "get_audio_dir",
    "get_raw_audio_file",
    "get_vocal_audio_file",
    "get_background_audio_file",
    "get_audio_refers_dir",
    "get_audio_segs_dir",
    "get_audio_tmp_dir",
]
