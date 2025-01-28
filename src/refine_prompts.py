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
    Покращує текст, роблячи його природнішим і враховуючи деталі про персонажа.
    
    Враховано:
    1. Використовувати першу особу (Я, Мені…).
    2. Додати 1–2 речення пояснення, чому персонаж не зацікавлений (відсутність дітей, пріоритет іншого хобі тощо).
    3. Пов’язати професію і хобі з його відмовою або байдужістю.
    4. Уникати повторів та надмірних ввічливих кліше.
    5. Текст має вміщуватися у 3–4 речення.
    6. Згадати контекст життя (місто/село, є діти/немає, характер).
    7. Якщо немає дітей, не використовувати відмову "У дитини немає часу".
    8. Характер (емпат/логік/інтроверт/екстраверт) відображати у тоні. 
    """

    system_prompt = """
Ти — сценарист, який перетворює сухі описи людей на короткі (3–4 речення) монологи від першої особи.

Правила:
1. Пиши «Я...» замість «Ти...».
2. Додай 1–2 речення про те, чому персонаж не хоче/не може займатися додатковими курсами (дітям не цікаво, немає дітей, завантаженість).
3. Зв’яжи професію або хобі з такою позицією (дизайнер цінує творчість, лікар має мало вільного часу, і т.д.).
4. Уникай повторів і формальних ввічливих фраз. 
5. Не перевищуй 3–4 речень. 
6. Якщо персонаж зазначений як «емпат», «логік», «інтроверт» чи «екстраверт» — відобрази це в тоні мовлення.
7. Якщо немає дітей, відмова «У дитини немає часу» нелогічна. Міняй на «Мені це не актуально» або «Немає для кого».
8. Якщо є діти, коротко згадай, чому саме вони не мають часу чи інтересу.
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
    """Читає промпти, покращує їх і зберігає у новий JSON."""
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