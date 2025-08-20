import json
import os
from ai.prompts import get_summary_prompt
import pandas as pd
from ai.utils import *
from ai.utils.path_constants import get_3_2_split_by_meaning, get_4_1_terminology
from ai.utils.workspace_utils import get_workspace_custom_terms_path

def combine_chunks(workspace_path: str = ".", config_path: str = None):
    """Combine the text chunks identified by whisper into a single long text"""
    input_file = get_3_2_split_by_meaning(workspace_path)
    with open(input_file, 'r', encoding='utf-8') as file:
        sentences = file.readlines()
    cleaned_sentences = [line.strip() for line in sentences]
    combined_text = ' '.join(cleaned_sentences)
    return combined_text[:load_key('summary_length', config_path)]  #! Return only the first x characters

def search_things_to_note_in_prompt(sentence, workspace_path: str = "."):
    """Search for terms to note in the given sentence"""
    terminology_file = get_4_1_terminology(workspace_path)
    if not os.path.exists(terminology_file):
        return None
        
    with open(terminology_file, 'r', encoding='utf-8') as file:
        things_to_note = json.load(file)
    things_to_note_list = [term['src'] for term in things_to_note['terms'] if term['src'].lower() in sentence.lower()]
    if things_to_note_list:
        prompt = '\n'.join(
            f'{i+1}. "{term["src"]}": "{term["tgt"]}",'
            f' meaning: {term["note"]}'
            for i, term in enumerate(things_to_note['terms'])
            if term['src'] in things_to_note_list
        )
        return prompt
    else:
        return None

def get_summary(workspace_path: str = ".", config_path: str = None):
    """
    요약 및 용어 추출
    
    Args:
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    output_file = get_4_1_terminology(workspace_path)
    
    # Check if output file already exists
    if os.path.exists(output_file):
        print(f"Output file already exists: {output_file}")
        return
    
    src_content = combine_chunks(workspace_path, config_path)
    
    # Load custom terms from workspace
    custom_terms_path = get_workspace_custom_terms_path(workspace_path)
    custom_terms = pd.read_excel(custom_terms_path) if os.path.exists(custom_terms_path) else pd.DataFrame()
    
    custom_terms_json = {
        "terms": 
            [
                {
                    "src": str(row.iloc[0]),
                    "tgt": str(row.iloc[1]), 
                    "note": str(row.iloc[2])
                }
                for _, row in custom_terms.iterrows()
            ]
    } 
    if len(custom_terms) > 0:
        rprint(f"📖 Custom Terms Loaded: {len(custom_terms)} terms")
        rprint("📝 Terms Content:", json.dumps(custom_terms_json, indent=2, ensure_ascii=False))
    summary_prompt = get_summary_prompt(src_content, custom_terms_json)
    rprint("📝 Summarizing and extracting terminology ...")
    
    def valid_summary(response_data):
        required_keys = {'src', 'tgt', 'note'}
        if 'terms' not in response_data:
            return {"status": "error", "message": "Invalid response format"}
        for term in response_data['terms']:
            if not all(key in term for key in required_keys):
                return {"status": "error", "message": "Invalid response format"}   
        return {"status": "success", "message": "Summary completed"}

    summary = ask_gpt(summary_prompt, resp_type='json', valid_def=valid_summary, workspace_path=workspace_path, config_path=config_path, log_title='summary')
    summary['terms'].extend(custom_terms_json['terms'])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)

    rprint(f'💾 Summary log saved to → `{output_file}`')

if __name__ == '__main__':
    get_summary()