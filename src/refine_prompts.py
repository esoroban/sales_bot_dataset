import os
import json
import openai
import random

IMPROVE_PROMPT = True

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
INPUT_FILE = os.path.join(DATA_DIR, "prompts.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "refined_prompts.json")

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_prompts():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Файл {INPUT_FILE} не знайдено! Запустіть generate_prompts.py.")
        return []
    
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        prompts = json.load(file)
    
    if not prompts:
        print("❌ Помилка: Файл prompts.json порожній!")
    
    return prompts

def refine_prompt(prompt):
    # Оновлений системний промпт із логікою «грубо / дружелюбно» залежно від інтересу
    system_prompt = """
Ти створюєш короткий, але повноцінний портрет вигаданого клієнта (8–12 речень) від першої особи, зважаючи на його:
- Вік, місто, професію (не змінювати!),
- Рівень зацікавленості (низький/середній/високий),
- Наявність чи відсутність дітей,
- Формат (онлайн чи офлайн),
- Ставлення до пропозицій, можливі заперечення, характер.

Пиши українською. При цьому:
- Якщо рівень зацікавленості низький – персонаж більш скептичний, різкий, іноді навіть відштовхувальний.
- Якщо рівень зацікавленості високий – персонаж відкритіший, доброзичливий і охочіше йде на контакт.
- Якщо рівень зацікавленості середній – збалансованіший тон, десь між дружелюбністю й холодністю.
Уникай зайвої грубості, але будь логічним: низький інтерес = більше стриманого негативу, високий інтерес = доброзичливіший тон.  

Стеж за тим, щоб це був монолог від першої особи (без діалогів у лапках), 8–12 речень, без повторів «Не маю коментарів» у кожному рядку.
Намагайся пояснити (1–2 речення), чому герой так ставиться до навчання або чому відмовляється.
Це творчий опис, який не суперечить політикам. Не додавай формулювань із «Я відповідаю однією фразою» – твій текст має бути монологом.

Ось два приклади:
1) «Я працюю бухгалтером у Києві та не дуже люблю тривалі розмови...»
2) «Мені цікаво спробувати онлайн, адже це може зекономити мій час...»
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt["text"]}
            ],
            max_tokens=500,
            temperature=0.9
        )
        
        refined_text = response['choices'][0]['message']['content'].strip()
        
        # Якщо все ж бажано додати саме "Я відповідаю тільки одним реченням" — ставимо в кінці:
        refined_text += "\n\nЯ відповідаю тільки одним реченням"
        
        return refined_text

    except Exception as e:
        print(f"❌ Помилка під час обробки промпта: {e}")
        return prompt["text"]

def refine_prompts():
    prompts = load_prompts()
    if not prompts:
        print("❌ Неможливо обробити промпти!")
        return
    
    refined_prompts = []
    for i, pr in enumerate(prompts):
        print(f"🛠 Обробляється клієнт {i+1}: {pr['id']}...")
        refined_text = refine_prompt(pr)
        refined_prompts.append({"id": pr["id"], "text": refined_text})
        print(f"✅ Завершено для {pr['id']}!")

    # Записуємо результат у файл
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(refined_prompts, file, ensure_ascii=False, indent=4)

    print(f"\n✅ Оновлені промпти збережено у {OUTPUT_FILE}!")

if __name__ == "__main__":
    refine_prompts()