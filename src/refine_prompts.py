import os
import json
import openai
import re

IMPROVE_PROMPT = True

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
INPUT_FILE = os.path.join(DATA_DIR, "prompts.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "refined_prompts.json")

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_prompts():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Файл {INPUT_FILE} не знайдено!")
        return []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        print("❌ Файл prompts.json порожній!")
    return data

def should_skip_improvement(text: str) -> bool:
    if "function_call" in text or re.search(r'\{\s*"?function_call"?\s*:', text):
        return True
    return False

def is_ukrainian_text(text: str) -> bool:
    ukr_chars = re.findall(r'[іїєґІЇЄҐ]', text, flags=re.IGNORECASE)
    return len(ukr_chars) > 0

def parse_interest_num(text: str) -> int:
    """
    Ищем в тексте 'Рівень зацікавлення: X' и пытаемся извлечь X как число.
    Если не нашли, возвращаем 0.
    """
    match = re.search(r"Рівень зацікавлення:\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return 0

def refine_prompt_logic(original_text: str) -> str:
    """
    Вносим дополнительную логику:
      - Если interest_num >= 3, добавляем строку о желании узнать цену.
      - Если interest_num >= 7, добавляем строку о желании записаться на промо.
    """
    interest_num = parse_interest_num(original_text)

    lines = original_text.split("\n")
    new_lines = []

    # Копируем исходные строки
    for line in lines:
        new_lines.append(line)

    # Добавляем строку о цене, если interest >= 3
    if interest_num >= 3:
        new_lines.append(
            "Оскільки твій інтерес не низький, ти можеш спочатку запитати «Скільки коштує?»."
        )

    # Добавляем строку о записи на промо, если interest >= 7
    if interest_num >= 7:
        new_lines.append(
            "Завдяки високому рівню інтересу, ти можеш одразу попросити «Запишіть мене» або сказати «Хочу спробувати»."
        )

    return "\n".join(new_lines)

def refine_prompt_with_gpt(text: str) -> str:
    if not IMPROVE_PROMPT:
        return text

    if should_skip_improvement(text):
        return text

    force_ukr = not is_ukrainian_text(text)

    system_prompt = """
Ти — коректор українською.
Отримуєш технічний сценарій (не діалог!) про людину.
1) Не змінюй факти (вік, кількість дітей, рівень зацікавленості).
2) Не вилучай списки реакцій або згадку про "Хочу спробувати" / "Запишіть мене".
3) Не перетворюй це на діалог.
4) Якщо текст не українською — перепиши його українською.
5) Зроби стиль природнішим, без вигаданих фактів.
""".strip()

    user_text = text
    if force_ukr:
        user_text = f"Оригінальний текст:\n{text}\n\nПерепиши, будь ласка, українською."

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            max_tokens=1200,
            temperature=0.7
        )
        refined = resp["choices"][0]["message"]["content"].strip()
        return refined
    except Exception as e:
        print(f"❌ Помилка GPT: {e}")
        return text

def refine_prompts():
    prompts = load_prompts()
    if not prompts:
        return

    refined_prompts = []
    for i, pr in enumerate(prompts):
        pid = pr.get("id", f"prompt_{i}")
        original_text = pr.get("text", "")
        print(f"➡ Обробляється {i+1}/{len(prompts)}: {pid}")

        # 1) Локальная логика: вставляем/добавляем строки в зависимости от interest
        logic_text = refine_prompt_logic(original_text)

        # 2) GPT-улучшение (не превращая в диалог)
        final_text = refine_prompt_with_gpt(logic_text)

        refined_prompts.append({"id": pid, "text": final_text})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(refined_prompts, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Збережено {len(refined_prompts)} оновлених промптів у {OUTPUT_FILE}!")

if __name__ == "__main__":
    refine_prompts()