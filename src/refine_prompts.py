import os
import json
import openai

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
    """
    Лише літературне полірування:
    - Не змінює фактів (вік, кількість дітей, професію тощо).
    - Розбиває на 1–2 абзаци, робить текст природнішим і легшим.
    - Додає 1–2 деталі атмосфери (згадка про природу, настрій тощо) без зміни фактів.
    - Обмежується до 8 речень.
    """
    
    system_prompt = """
Ти — сценарист і коректор українською.
Отримуєш монолог від першої особи про людину (вік, професія, кількість дітей тощо).
Не змінюй жодних фактів і чисел (вік, кількість дітей, рівень зацікавленості, спосіб життя).
Твоє завдання:
1) Зроби текст легшим і природнішим: усунь надмірну сухість чи повтори.
2) Допусти 1–2 короткі деталі атмосфери (наприклад, про сільську місцевість або міський шум), що не суперечать фактам.
3) Розбий максимум на 2 абзаци, загалом не більше 8 речень.
4) Не придумуй нових обставин (не додавай вигаданих хобі, дітей чи чисел).
"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt["text"]}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
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

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(refined_prompts, file, ensure_ascii=False, indent=4)

    print(f"\n✅ Оновлені промпти збережено у {OUTPUT_FILE}!")

if __name__ == "__main__":
    refine_prompts()