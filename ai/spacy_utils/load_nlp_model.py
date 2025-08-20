import spacy
from spacy.cli import download
from ai.utils import rprint, load_key, except_handler

def get_spacy_model(language: str, config_path: str = None):
    spacy_model_map = load_key("spacy_model_map", config_path)
    model = spacy_model_map.get(language.lower(), "en_core_web_md")
    if language not in spacy_model_map:
        rprint(f"[yellow]Spacy model does not support '{language}', using en_core_web_md model as fallback...[/yellow]")
    return model

@except_handler("Failed to load NLP Spacy model")
def init_nlp(config_path: str = None):
    """
    NLP 모델 초기화
    
    Args:
        config_path: Path to config file (optional)
    """
    language = "en" if load_key("whisper.language", config_path) == "en" else load_key("whisper.detected_language", config_path)
    model = get_spacy_model(language, config_path)
    rprint(f"[blue]⏳ Loading NLP Spacy model: <{model}> ...[/blue]")
    try:
        nlp = spacy.load(model)
    except:
        rprint(f"[yellow]Downloading {model} model...[/yellow]")
        rprint("[yellow]If download failed, please check your network and try again.[/yellow]")
        download(model)
        nlp = spacy.load(model)
    rprint("[green]✅ NLP Spacy model loaded successfully![/green]")
    return nlp
