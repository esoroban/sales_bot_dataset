import os
import json
import openai

# Пути к файлам
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
INPUT_FILE = os.path.join(DATA_DIR, "prompts.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "refined_prompts.json")

# Загрузка API-ключа
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_prompts():
    """Завантажує список клієнтів з prompts.json"""
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Файл {INPUT_FILE} не знайдено! Запустіть generate_prompts.py.")
        return []
    
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        prompts = json.load(file)
    
    if not prompts:
        print("❌ Помилка: Файл prompts.json порожній!")
    
    return prompts

def refine_prompt(prompt):
    """Літературно покращує текст, додаючи природності"""
    system_prompt = """
    Ти сценарист, який створює живих персонажів для діалогів.
    Ти отримуєш початковий опис клієнта і маєш переписати його так, щоб він звучав максимально природно.
    
    🔹 Важливо:
    1. Пиши **від першої особи** (Я, Мені, У мене...).
    2. Не змінюй зміст, тільки додавай живості, змушуй текст "дихати".
    3. Тон має відповідати стилю розмови персонажа (грубий, саркастичний, ввічливий тощо).
    4. Відповіді мають бути **короткими, до 3-4 речень**.
    
    📌 **Приклад**  
    **Було:**  
    "Ти Іван, тобі 24. Ти механік, захоплюєшся футболом. Твій характер — інтроверт."  
      
    **Стало:**  
    "Я Іван, мені 24. Я механік, постійно кручуся біля авто. Люблю футбол, але більше спостерігати, ніж грати. Я не люблю довгі розмови, волію сказати прямо, що думаю."
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
        print(f"❌ Ошибка при обробці промпта: {e}")
        return prompt["text"]

def refine_prompts():
    """Читає промпти, покращує їх і зберігає у новий JSON"""
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