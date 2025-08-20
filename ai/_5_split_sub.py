import pandas as pd
from typing import List, Tuple
import concurrent.futures
import os

from ai._3_2_split_meaning import split_sentence
from ai.prompts import get_align_prompt
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from ai.utils import *
from ai.utils.path_constants import get_4_2_translation, get_5_split_sub, get_5_remerged

console = Console()

# ! You can modify your own weights here
# Chinese and Japanese 2.5 characters, Korean 2 characters, Thai 1.5 characters, full-width symbols 2 characters, other English-based and half-width symbols 1 character
def calc_len(text: str) -> float:
    text = str(text) # force convert
    def char_weight(char):
        code = ord(char)
        if 0x4E00 <= code <= 0x9FFF or 0x3040 <= code <= 0x30FF:  # Chinese and Japanese
            return 1.75
        elif 0xAC00 <= code <= 0xD7A3 or 0x1100 <= code <= 0x11FF:  # Korean
            return 1.5
        elif 0x0E00 <= code <= 0x0E7F:  # Thai
            return 1
        elif 0xFF01 <= code <= 0xFF5E:  # full-width symbols
            return 1.75
        else:  # other characters (e.g. English and half-width symbols)
            return 1

    return sum(char_weight(char) for char in text)

def align_subs(src_sub: str, tr_sub: str, src_part: str, workspace_path: str = ".", config_path: str = None) -> Tuple[List[str], List[str], str]:
    align_prompt = get_align_prompt(src_sub, tr_sub, src_part, config_path)
    
    def valid_align(response_data):
        if 'align' not in response_data:
            return {"status": "error", "message": "Missing required key: `align`"}
        if len(response_data['align']) < 2:
            return {"status": "error", "message": "Align does not contain more than 1 part as expected!"}
        return {"status": "success", "message": "Align completed"}
    parsed = ask_gpt(align_prompt, resp_type='json', valid_def=valid_align, workspace_path=workspace_path, config_path=config_path, log_title='align_subs')
    align_data = parsed['align']
    src_parts = src_part.split('\n')
    tr_parts = [item[f'target_part_{i+1}'].strip() for i, item in enumerate(align_data)]
    
    whisper_language = load_key("whisper.language", config_path)
    language = load_key("whisper.detected_language", config_path) if whisper_language == 'auto' else whisper_language
    joiner = get_joiner(language, config_path)
    tr_remerged = joiner.join(tr_parts)
    
    table = Table(title="🔗 Aligned parts")
    table.add_column("Language", style="cyan")
    table.add_column("Parts", style="magenta")
    table.add_row("SRC_LANG", "\n".join(src_parts))
    table.add_row("TARGET_LANG", "\n".join(tr_parts))
    console.print(table)
    
    return src_parts, tr_parts, tr_remerged

def split_align_subs(src_lines: List[str], tr_lines: List[str], config_path: str = None):
    subtitle_set = load_key("subtitle", config_path)
    MAX_SUB_LENGTH = subtitle_set["max_length"]
    TARGET_SUB_MULTIPLIER = subtitle_set["target_multiplier"]
    remerged_tr_lines = tr_lines.copy()
    
    to_split = []
    for i, (src, tr) in enumerate(zip(src_lines, tr_lines)):
        src, tr = str(src), str(tr)
        if len(src) > MAX_SUB_LENGTH or calc_len(tr) * TARGET_SUB_MULTIPLIER > MAX_SUB_LENGTH:
            to_split.append(i)
            table = Table(title=f"📏 Line {i} needs to be split")
            table.add_column("Type", style="cyan")
            table.add_column("Content", style="magenta")
            table.add_row("Source Line", src)
            table.add_row("Target Line", tr)
            console.print(table)
    
    @except_handler("Error in split_align_subs")
    def process(i):
        split_src = split_sentence(src_lines[i], num_parts=2, config_path=config_path).strip()
        src_parts, tr_parts, tr_remerged = align_subs(src_lines[i], tr_lines[i], split_src, workspace_path, config_path)
        src_lines[i] = src_parts
        tr_lines[i] = tr_parts
        remerged_tr_lines[i] = tr_remerged
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=load_key("max_workers", config_path)) as executor:
        executor.map(process, to_split)
    
    # Flatten `src_lines` and `tr_lines`
    src_lines = [item for sublist in src_lines for item in (sublist if isinstance(sublist, list) else [sublist])]
    tr_lines = [item for sublist in tr_lines for item in (sublist if isinstance(sublist, list) else [sublist])]
    
    return src_lines, tr_lines, remerged_tr_lines

def split_for_sub_main(workspace_path: str = ".", config_path: str = None):
    """
    자막용 텍스트 분할
    
    Args:
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    output_file = get_5_split_sub(workspace_path)
    remerged_file = get_5_remerged(workspace_path)
    
    # Check if output file already exists
    if os.path.exists(output_file):
        print(f"Output file already exists: {output_file}")
        return
    
    console.print("[bold green]🚀 Start splitting subtitles...[/bold green]")
    
    df = pd.read_excel(get_4_2_translation(workspace_path))
    src = df['Source'].tolist()
    trans = df['Translation'].tolist()
    
    subtitle_set = load_key("subtitle", config_path)
    MAX_SUB_LENGTH = subtitle_set["max_length"]
    TARGET_SUB_MULTIPLIER = subtitle_set["target_multiplier"]
    
    for attempt in range(3):  # Multiple cutting
        console.print(Panel(f"🔄 Split attempt {attempt + 1}", expand=False))
        split_src, split_trans, remerged = split_align_subs(src.copy(), trans, config_path)
        
        # Check if all subtitles meet the length requirements
        if all(len(src) <= MAX_SUB_LENGTH for src in split_src) and \
           all(calc_len(tr) * TARGET_SUB_MULTIPLIER <= MAX_SUB_LENGTH for tr in split_trans):
            break
        
        # Update source data to continue the next round of segmentation
        src, trans = split_src, split_trans

    # Make sure they have the same length to avoid errors.
    if len(src) > len(remerged):
        remerged += [None] * (len(src) - len(remerged))
    elif len(remerged) > len(src):
        src += [None] * (len(remerged) - len(src))
    
    pd.DataFrame({'Source': split_src, 'Translation': split_trans}).to_excel(output_file, index=False)
    pd.DataFrame({'Source': src, 'Translation': remerged}).to_excel(remerged_file, index=False)

if __name__ == '__main__':
    split_for_sub_main()
