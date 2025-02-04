import os
import json
import openai

# Шлях до файлів
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
INPUT_FILE = os.path.join(DATA_DIR, "prompts.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "refined_prompts.json")

# Завантаження API-ключа
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_prompts():
    """Завантажує список клієнтів з prompts.json."""
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
    Лише літературно покращує та додає легку фантазійність до сирого тексту:
    - Не змінює фактаж (вік, професію, наявність дітей).
    - Підправляє граматику та синтаксис.
    - Додає 1–2 пропозиції, що роблять текст живішим (емоційний штрих, атмосфера).
    - Обмежується 6 реченнями максимум.
    """

    system_prompt = """
Ти — сценарист і редактор українською, що робить монолог від першої особи більш красивим і трохи емоційним. 
При цьому ти НЕ змінюєш факти, закладені в тексті (вік, професію, наявність чи вік дітей, причину відмови). 
Твої завдання:
1. Залишити обсяг до 12 речень.
2. Прибрати повтори, очевидні помилки й канцеляризми.
3. Додати легку фантазійну деталь (1–2 речення про настрій чи оточення), що не суперечить фактам.
4. Не вводити нових фактів, які повністю змінюють зміст (напр. не вигадуй іншу причину відмови).
5. Мова — природна, жвава, без надмірної ввічливості.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt["text"]}
            ],
            max_tokens=500,
            temperature=0.8  # трішки підвищена креативність
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"❌ Помилка під час обробки промпта: {e}")
        return prompt["text"]

def refine_prompts():
    """Читає промпти, покращує їх стилістично/літературно і зберігає в refined_prompts.json."""
    prompts = load_prompts()
    if not prompts:
        print("❌ Неможливо обробити промпти!")
        return
    
    refined_prompts = []

    for i, prompt in enumerate(prompts):
        print(f"🛠 Обробляється клієнт {i+1}: {prompt['id']}...")
        refined_text = refine_prompt(prompt)
        refined_prompts.append({"id": prompt["id"], "text": refined_text})
        print(f"✅ Завершено для {prompt['id']}!")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(refined_prompts, file, ensure_ascii=False, indent=4)

    print(f"\n✅ Оновлені промпти збережено у {OUTPUT_FILE}!")

if __name__ == "__main__":
    refine_prompts()