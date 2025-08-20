import os
import string
import warnings
from ai.spacy_utils.load_nlp_model import init_nlp
from ai.utils import *
from ai.utils.path_constants import get_3_1_split_by_nlp

warnings.filterwarnings("ignore", category=FutureWarning)

def split_long_sentence(doc, config_path: str = None):
    tokens = [token.text for token in doc]
    n = len(tokens)
    
    # dynamic programming array, dp[i] represents the optimal split scheme from the start to the ith token
    dp = [float('inf')] * (n + 1)
    dp[0] = 0
    
    # record optimal split points
    prev = [0] * (n + 1)
    
    for i in range(1, n + 1):
        for j in range(max(0, i - 100), i):  # limit search range to avoid overly long sentences
            if i - j >= 30:  # ensure sentence length is at least 30
                token = doc[i-1]
                if j == 0 or (token.is_sent_end or token.pos_ in ['VERB', 'AUX'] or token.dep_ == 'ROOT'):
                    if dp[j] + 1 < dp[i]:
                        dp[i] = dp[j] + 1
                        prev[i] = j
    
    # rebuild sentences based on optimal split points
    sentences = []
    i = n
    whisper_language = load_key("whisper.language", config_path)
    language = load_key("whisper.detected_language", config_path) if whisper_language == 'auto' else whisper_language # consider force english case
    joiner = get_joiner(language, config_path)
    while i > 0:
        j = prev[i]
        sentences.append(joiner.join(tokens[j:i]).strip())
        i = j
    
    return sentences[::-1]  # reverse list to keep original order

def split_extremely_long_sentence(doc, config_path: str = None):
    tokens = [token.text for token in doc]
    n = len(tokens)
    
    num_parts = (n + 59) // 60  # round up
    
    part_length = n // num_parts
    
    sentences = []
    whisper_language = load_key("whisper.language", config_path)
    language = load_key("whisper.detected_language", config_path) if whisper_language == 'auto' else whisper_language # consider force english case
    joiner = get_joiner(language, config_path)
    for i in range(num_parts):
        start = i * part_length
        end = start + part_length if i < num_parts - 1 else n
        sentence = joiner.join(tokens[start:end])
        sentences.append(sentence)
    
    return sentences


def split_long_by_root_main(nlp, workspace_path: str = ".", config_path: str = None):
    """
    긴 문장을 루트 기반으로 분할
    
    Args:
        nlp: Spacy NLP model
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    split_by_connector_file = f"{workspace_path}/output/log/split_by_connector.txt"
    output_file = get_3_1_split_by_nlp(workspace_path)
    
    with open(split_by_connector_file, "r", encoding="utf-8") as input_file:
        sentences = input_file.readlines()

    all_split_sentences = []
    for sentence in sentences:
        doc = nlp(sentence.strip())
        if len(doc) > 60:
            split_sentences = split_long_sentence(doc, config_path)
            if any(len(nlp(sent)) > 60 for sent in split_sentences):
                split_sentences = [subsent for sent in split_sentences for subsent in split_extremely_long_sentence(nlp(sent), config_path)]
            all_split_sentences.extend(split_sentences)
            rprint(f"[yellow]✂️  Splitting long sentences by root: {sentence[:30]}...[/yellow]")
        else:
            all_split_sentences.append(sentence.strip())

    punctuation = string.punctuation + "'" + '"'  # include all punctuation and apostrophe ' and "

    with open(output_file, "w", encoding="utf-8") as output_file_handle:
        for i, sentence in enumerate(all_split_sentences):
            stripped_sentence = sentence.strip()
            if not stripped_sentence or all(char in punctuation for char in stripped_sentence):
                rprint(f"[yellow]⚠️  Warning: Empty or punctuation-only line detected at index {i}[/yellow]")
                if i > 0:
                    all_split_sentences[i-1] += sentence
                continue
            output_file_handle.write(sentence + "\n")

    # delete the original file
    os.remove(split_by_connector_file)   

    rprint(f"[green]💾 Long sentences split by root saved to →  {output_file}[/green]")

if __name__ == "__main__":
    nlp = init_nlp()
    split_long_by_root_main(nlp)
    # raw = ""
    # nlp = init_nlp()
    # doc = nlp(raw.strip())
    # for sent in split_still_long_sentence(doc):
    #     print(sent, '\n==========')
