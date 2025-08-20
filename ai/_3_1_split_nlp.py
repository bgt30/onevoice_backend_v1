from ai.spacy_utils import *
from ai.utils.path_constants import get_3_1_split_by_nlp
import os

def split_by_spacy(workspace_path: str = ".", config_path: str = None):
    """
    NLP 기반 텍스트 분할
    
    Args:
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
    """
    output_file = get_3_1_split_by_nlp(workspace_path)
    
    # Check if output file already exists
    if os.path.exists(output_file):
        print(f"Output file already exists: {output_file}")
        return
    
    nlp = init_nlp(config_path)
    split_by_mark(nlp, workspace_path, config_path)
    split_by_comma_main(nlp, workspace_path, config_path)
    split_sentences_main(nlp, workspace_path, config_path)
    split_long_by_root_main(nlp, workspace_path, config_path)
    return

if __name__ == '__main__':
    split_by_spacy()