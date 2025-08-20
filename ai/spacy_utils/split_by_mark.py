import os
import pandas as pd
import warnings
from ai.spacy_utils.load_nlp_model import init_nlp
from ai.utils.config_utils import load_key, get_joiner
from ai.utils.path_constants import get_2_cleaned_chunks
from rich import print as rprint

warnings.filterwarnings("ignore", category=FutureWarning)

def split_by_mark(nlp, workspace_path: str = ".", config_path: str = None):
    """
    구두점 기반 텍스트 분할
    
    Args:
        nlp: Spacy NLP model
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    whisper_language = load_key("whisper.language", config_path)
    language = load_key("whisper.detected_language", config_path) if whisper_language == 'auto' else whisper_language # consider force english case
    joiner = get_joiner(language, config_path)
    rprint(f"[blue]🔍 Using {language} language joiner: '{joiner}'[/blue]")
    
    cleaned_chunks_file = get_2_cleaned_chunks(workspace_path)
    chunks = pd.read_excel(cleaned_chunks_file)
    chunks.text = chunks.text.apply(lambda x: x.strip('"').strip(""))
    
    # join with joiner
    input_text = joiner.join(chunks.text.to_list())

    doc = nlp(input_text)
    assert doc.has_annotation("SENT_START")

    # skip - and ...
    sentences_by_mark = []
    current_sentence = []
    
    # iterate all sentences
    for sent in doc.sents:
        text = sent.text.strip()
        
        # check if the current sentence ends with - or ...
        if current_sentence and (
            text.startswith('-') or 
            text.startswith('...') or
            current_sentence[-1].endswith('-') or
            current_sentence[-1].endswith('...')
        ):
            current_sentence.append(text)
        else:
            if current_sentence:
                sentences_by_mark.append(' '.join(current_sentence))
                current_sentence = []
            current_sentence.append(text)
    
    # add the last sentence
    if current_sentence:
        sentences_by_mark.append(' '.join(current_sentence))

    split_by_mark_file = f"{workspace_path}/output/log/split_by_mark.txt"
    with open(split_by_mark_file, "w", encoding="utf-8") as output_file:
        for i, sentence in enumerate(sentences_by_mark):
            if i > 0 and sentence.strip() in [',', '.', '，', '。', '？', '！']:
                # ! If the current line contains only punctuation, merge it with the previous line, this happens in Chinese, Japanese, etc.
                output_file.seek(output_file.tell() - 1, os.SEEK_SET)  # Move to the end of the previous line
                output_file.write(sentence)  # Add the punctuation
            else:
                output_file.write(sentence + "\n")
    
    rprint(f"[green]💾 Sentences split by punctuation marks saved to →  `{split_by_mark_file}`[/green]")

if __name__ == "__main__":
    nlp = init_nlp()
    split_by_mark(nlp)
