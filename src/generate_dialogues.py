import os
import json
import uuid
import openai
import random

# Шляхи до файлів
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PROMPTS_FILE = os.path.join(DATA_DIR, "refined_prompts.json")
DIALOGUES_FILE = os.path.join(DATA_DIR, "dialogues.json")
BOT_PROMPT_FILE = os.path.join(DATA_DIR, "bot_prompt.txt")

NUM_DIALOGUES = 2        # Скільки діалогів згенерувати
NUM_EXCHANGES = 5        # Скільки обмінів бот-клієнт максимально

# Відповіді клієнта при відсутності інтересу
NO_INTEREST_RESPONSES = [
    "Мені це не потрібно.",
    "Не цікаво.",
    "У мене інші плани.",
    "Я не думаю, що це корисно.",
    "Я не шукаю подібного."
]

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_file(file_path):
    """Читає вміст текстового файлу (для bot_prompt)."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено!")
        return ""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()

def load_prompts(file_path):
    """Завантажує список промптів (клієнтських) із JSON."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено!")
        return []
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not data:
        print("❌ Файл із промптами порожній!")
    return data

def generate_bot_response(bot_context):
    """
    Генерує відповідь БОТА (assistant) на основі bot_context.
    bot_context — список повідомлень: system (bot_prompt) + черга 'assistant' / 'user'.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=bot_context,
            max_tokens=300,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"❌ Помилка при генерації відповіді БОТА: {e}")
        return ""

def generate_client_response(client_context):
    """
    Генерує відповідь КЛІЄНТА (assistant) на основі client_context.
    client_context — список повідомлень: system (мінімальна інструкція для клієнта) + user/assistant.
    У user: повідомлення від бота.
    У assistant: повідомлення клієнта.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=client_context,
            max_tokens=300,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"❌ Помилка при генерації відповіді КЛІЄНТА: {e}")
        return ""

def create_dialogue(prompt, bot_prompt):
    """
    Створює діалог між:
      - Ботом (bot_context)
      - Клієнтом (client_context),
    де prompt["text"] — це початковий опис клієнта з refined_prompts.json,
    bot_prompt — це системний prompt для бота (текст із файлу).
    """

    conversation_id = str(uuid.uuid4())
    dialogue = {
        "conversation_id": conversation_id,
        "dialogue": []
    }

    # Визначимо, чи немає інтересу (ключова ознака: "немає інтересу" у тексті)
    if "немає інтересу" in prompt["text"]:
        interest_level = "немає інтересу"
    else:
        interest_level = "слабкий інтерес"  # умовно

    # ----------------------
    # 1. Ініціалізуємо контексти

    # Бот (sales_bot)
    bot_context = [
        {"role": "system", "content": bot_prompt}
    ]

    # Клієнт (Client)
    # Він отримає мінімальний system-підказ: не дублюй пропозицію, не пропонуй допомогу...
    client_system_prompt = """
Ти — звичайний клієнт, який не пропонує допомогу та не дублює пропозиції бота.
Використовуй інформацію зі свого початкового опису, але відповідай стисло.
"""
    client_context = [
        {"role": "system", "content": client_system_prompt},
        # Додаємо початковий опис із refined_prompts.json у ролі user?
        # Ні, зазвичай це опис клієнта. Для простоти можна додати як assistant,
        # або лишити як коментар. Основне: prompt["text"] — це бекґраунд, 
        # якби внутрішній стан клієнта.
    ]

    # ----------------------
    # 2. Перше повідомлення бота
    first_bot_message = "Вітаю! Чи цікаво дізнатися про наші курси математики для дітей 5–12 років?"
    bot_context.append({"role": "assistant", "content": first_bot_message})

    dialogue["dialogue"].append({"role": "sales_bot", "message": first_bot_message})
    print(f"[Бот]: {first_bot_message}")

    # ----------------------
    # 3. Клієнт реагує (перша відповідь)
    # Для клієнта це вхід, отже client_context + last bot message у ролі "user"
    client_context.append({"role": "user", "content": first_bot_message})

    # Тут можна "підмішати" prompt["text"] як «пам’ять клієнта», 
    # наприклад, додати у system або assistant. 
    # Але найпростіше — вважати, що prompt["text"] це внутрішній опис клієнта, 
    # який впливає на його стиль. Можна додати в system?
    # Або додати: client_context.append({"role":"assistant","content": prompt["text"]})
    # якщо хочемо, щоб ШІ це бачив як «задник».
    client_context.append({"role": "assistant", "content": prompt["text"]})

    # Тепер генеруємо відповідь
    client_reply = generate_client_response(client_context)
    if not client_reply:
        print("❌ Помилка: клієнт не згенерував відповіді (перший крок).")
        return None

    # Записуємо в діалог
    dialogue["dialogue"].append({"role": "client", "message": client_reply})
    print(f"[Клієнт]: {client_reply}")

    # Оновлюємо client_context: 
    # — клієнт уже відповів, тож це його "assistant" повідомлення
    client_context.append({"role": "assistant", "content": client_reply})
    # Бот бачить це як "user"
    bot_context.append({"role": "user", "content": client_reply})

    # ----------------------
    # 4. Подальші обміни
    for i in range(NUM_EXCHANGES):
        # Якщо у нас "немає інтересу" — завершуємо швидко
        if interest_level == "немає інтересу":
            client_response = random.choice(NO_INTEREST_RESPONSES)
            dialogue["dialogue"].append({"role": "client", "message": client_response})
            print(f"[Клієнт]: {client_response} (немає інтересу)\n")
            break

        # Відповідь бота
        bot_ans = generate_bot_response(bot_context)
        if not bot_ans:
            print("❌ Помилка: бот не згенерував відповідь!")
            break

        # Записуємо в діалог
        dialogue["dialogue"].append({"role": "sales_bot", "message": bot_ans})
        print(f"[Бот]: {bot_ans}")

        # Додаємо в bot_context
        bot_context.append({"role": "assistant", "content": bot_ans})

        # Тепер клієнт
        client_context.append({"role": "user", "content": bot_ans})
        client_ans = generate_client_response(client_context)
        if not client_ans:
            print("❌ Помилка: клієнт не згенерував відповідь!")
            break

        dialogue["dialogue"].append({"role": "client", "message": client_ans})
        print(f"[Клієнт]: {client_ans}\n")

        # оновимо контексти
        client_context.append({"role": "assistant", "content": client_ans})
        bot_context.append({"role": "user", "content": client_ans})

    # Перевірка на мінімальну кількість
    if len(dialogue["dialogue"]) < 2:
        print("❌ Помилка: Діалог замалий.")
        return None

    return dialogue

def save_dialogues(dialogues, file_path):
    """Зберігає діалоги у JSON-файл."""
    if not dialogues:
        print("❌ Немає діалогів для збереження.")
        return

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dialogues, f, ensure_ascii=False, indent=4)
        print(f"\n✅ Діалоги збережено у {file_path}.")
    except Exception as e:
        print(f"❌ Помилка при збереженні файлу: {e}")

def main():
    prompts = load_prompts(PROMPTS_FILE)
    bot_prompt = load_file(BOT_PROMPT_FILE)

    if not prompts or not bot_prompt:
        print("❌ Немає даних для створення діалогів!")
        return

    dialogues = []
    for i, prompt in enumerate(prompts[:NUM_DIALOGUES]):
        print(f"\n🛠 Генерується діалог {i+1} для клієнта {prompt['id']}...\n")
        dialogue = create_dialogue(prompt, bot_prompt)
        if dialogue:
            dialogues.append(dialogue)

    print(f"\n🔍 Отримано {len(dialogues)} діалог(и).")
    save_dialogues(dialogues, DIALOGUES_FILE)

if __name__ == "__main__":
    main()