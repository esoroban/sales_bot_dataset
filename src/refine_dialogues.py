import os
import json
import openai
import re
from dotenv import load_dotenv

# Константа, управляющая улучшением диалогов:
REFINE_DIALOGUES = True

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
INPUT_FILE = os.path.join(DATA_DIR, "dialogues.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "refined_dialogues.json")
PROMPT_FILE = os.path.join(DATA_DIR, "refine_prompt.txt")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_dialogues():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Файл {INPUT_FILE} не знайдено!")
        return []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def should_skip_dialogue(text: str) -> bool:
    return "function_call" in text or re.search(r'\{\s*"?function_call"?\s*:', text)

def load_prompt() -> str:
    if not os.path.exists(PROMPT_FILE):
        raise FileNotFoundError(f"❌ Файл з промптом {PROMPT_FILE} не знайдено!")
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def extract_json(text):
    try:
        json_str = re.search(r'(\[.*\])', text, re.DOTALL).group(1)
        return json.loads(json_str)
    except (AttributeError, json.JSONDecodeError):
        return None

def refine_dialogue_with_gpt(dialogue: str, system_prompt: str) -> str:
    if not REFINE_DIALOGUES or should_skip_dialogue(dialogue):
        return dialogue

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": dialogue}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        refined = response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"❌ Помилка GPT: {e}")
        refined = dialogue

    return refined

def refine_dialogues():
    dialogues = load_dialogues()
    if not dialogues:
        return

    system_prompt = load_prompt()

    refined_dialogues = []
    for i, dlg in enumerate(dialogues):
        dialogue_id = dlg.get("conversation_id", f"dialogue_{i}")
        print(f"➡ Обробляється {i+1}/{len(dialogues)}: {dialogue_id}")

        dialogue_content = json.dumps(dlg["dialogue"], ensure_ascii=False, indent=2)

        refined_content = refine_dialogue_with_gpt(dialogue_content, system_prompt)

        refined_dialogue_json = extract_json(refined_content)

        if refined_dialogue_json is None:
            print(f"❌ Некоректний JSON, повертаємо вихідний діалог для {dialogue_id}")
            refined_dialogue_json = dlg["dialogue"]

        refined_dialogues.append({
            "conversation_id": dialogue_id,
            "dialogue": refined_dialogue_json
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(refined_dialogues, f, ensure_ascii=False, indent=4)

    print(f"✅ Збережено {len(refined_dialogues)} покращених діалогів у {OUTPUT_FILE}!")

if __name__ == "__main__":
    refine_dialogues()