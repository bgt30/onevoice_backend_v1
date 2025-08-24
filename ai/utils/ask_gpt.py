import os
import json
from threading import Lock
import json_repair
from openai import OpenAI
from ai.utils.config_utils import load_key
from rich import print as rprint
from ai.utils.decorator import except_handler

# ------------
# cache gpt response
# ------------

LOCK = Lock()

def _save_cache(model, prompt, resp_content, resp_type, resp, workspace_path: str = ".", message=None, log_title="default"):
    with LOCK:
        logs = []
        gpt_log_folder = f"{workspace_path}/output/gpt_log"
        file = os.path.join(gpt_log_folder, f"{log_title}.json")
        os.makedirs(os.path.dirname(file), exist_ok=True)
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        logs.append({"model": model, "prompt": prompt, "resp_content": resp_content, "resp_type": resp_type, "resp": resp, "message": message})
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)

def _load_cache(prompt, resp_type, workspace_path: str = ".", log_title="default"):
    with LOCK:
        gpt_log_folder = f"{workspace_path}/output/gpt_log"
        file = os.path.join(gpt_log_folder, f"{log_title}.json")
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                for item in json.load(f):
                    if item["prompt"] == prompt and item["resp_type"] == resp_type:
                        return item["resp"]
        return False

# ------------
# ask gpt once
# ------------

@except_handler("GPT request failed", retry=5)
def ask_gpt(prompt, resp_type=None, valid_def=None, workspace_path: str = ".", config_path: str = None, log_title="default"):
    """
    GPT API 호출
    
    Args:
        prompt: Input prompt
        resp_type: Response type (json, text, etc.)
        valid_def: Validation function
        workspace_path: Path to workspace directory
        config_path: Path to config file (optional)
        log_title: Log title for caching
    """
    if not load_key("api.key", config_path):
        raise ValueError("API key is not set")
    # check cache
    cached = _load_cache(prompt, resp_type, workspace_path, log_title)
    if cached:
        rprint("use cache response")
        return cached

    model = load_key("api.model", config_path)
    client = OpenAI(api_key=load_key("api.key", config_path))
    response_format = {"type": "json_object"} if resp_type == "json" and load_key("api.llm_support_json", config_path) else None

    messages = [{"role": "user", "content": prompt}]

    params = dict(
        model=model,
        messages=messages,
        response_format=response_format,
        timeout=900,
        service_tier="flex",
    )
    resp_raw = client.chat.completions.create(**params)

    # process and return full result
    resp_content = resp_raw.choices[0].message.content
    if resp_type == "json":
        resp = json_repair.loads(resp_content)
    else:
        resp = resp_content
    
    # check if the response format is valid
    if valid_def:
        valid_resp = valid_def(resp)
        if valid_resp['status'] != 'success':
            _save_cache(model, prompt, resp_content, resp_type, resp, workspace_path, log_title="error", message=valid_resp['message'])
            raise ValueError(f"❎ API response error: {valid_resp['message']}")

    _save_cache(model, prompt, resp_content, resp_type, resp, workspace_path, log_title=log_title)
    return resp


if __name__ == '__main__':
    from rich import print as rprint
    
    result = ask_gpt("""test respond ```json\n{\"code\": 200, \"message\": \"success\"}\n```""", resp_type="json")
    rprint(f"Test json output result: {result}")
