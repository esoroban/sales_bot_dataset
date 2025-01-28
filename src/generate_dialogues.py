import os
import json
import uuid
import openai
import random

# Пути к файлам
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PROMPTS_FILE = os.path.join(DATA_DIR, "refined_prompts.json")  # Використовуємо prompts.json
DIALOGUES_FILE = os.path.join(DATA_DIR, "dialogues.json")
BOT_PROMPT_FILE = os.path.join(DATA_DIR, "bot_prompt.txt")

# Константи
NUM_DIALOGUES = 10
NUM_EXCHANGES = 10

# Можливі відповіді клієнта при відсутності інтересу
NO_INTEREST_RESPONSES = [
    "Мені це не потрібно.",
    "Не цікаво.",
    "У мене інші плани.",
    "Я не думаю, що це корисно.",
    "Я не шукаю подібного."
]

# Завантаження API-ключа
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_file(file_path):
    """Читає вміст текстового файлу."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено!")
        return ""

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()

def load_prompts(file_path):
    """Завантажує список промптів клієнтів у форматі JSON."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено!")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        prompts = json.load(file)

    if not prompts:
        print("❌ Помилка: Файл промптів порожній!")

    return prompts

def generate_ai_response(messages):
    """Генерує відповідь OpenAI з урахуванням попередніх реплік."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"❌ Помилка при генерації відповіді: {e}")
        return ""

def create_dialogue(prompt, bot_prompt):
    """Створює діалог між ботом та клієнтом на основі його промпту."""
    conversation_id = str(uuid.uuid4())
    dialogue_history = []

    # Витягуємо рівень інтересу клієнта
    interest_level = "немає інтересу" if "немає інтересу" in prompt["text"] else "слабкий інтерес"

    # Базове привітання без згадки про дітей
    bot_greeting = "Вітаю! Чи цікавитесь розвитком когнітивних навичок?"

    bot_messages = [
        {"role": "system", "content": bot_prompt},
        {"role": "assistant", "content": bot_greeting}
    ]

    client_messages = [
        {"role": "system", "content": "Ти звичайний клієнт. Відповідай згідно свого стилю."},
        {"role": "user", "content": prompt["text"]}
    ]

    dialogue = {
        "conversation_id": conversation_id,
        "dialogue": []
    }

    print(f"\n=== 🔵 Генерація діалогу для клієнта {prompt['id']} ===\n")

    for i in range(NUM_EXCHANGES):
        # Відповідь бота
        bot_response = generate_ai_response(bot_messages + dialogue_history)
        if not bot_response:
            print("❌ Помилка: Бот не сгенерував відповідь!")
            continue

        dialogue_history.append({"role": "assistant", "content": bot_response})
        dialogue["dialogue"].append({"role": "sales_bot", "message": bot_response})
        print(f"🤖 Бот: {bot_response}")

        # Перевірка рівня інтересу клієнта
        if interest_level == "немає інтересу":
            client_response = random.choice(NO_INTEREST_RESPONSES)  # Обираємо випадкову відповідь
            dialogue["dialogue"].append({"role": "client", "message": client_response})
            print(f"🧑‍💼 Клієнт: {client_response}\n")
            break  # Якщо інтересу немає, розмова завершується швидше

        # Відповідь клієнта
        client_messages.append({"role": "user", "content": bot_response})
        client_response = generate_ai_response(client_messages + dialogue_history)

        if not client_response or client_response == bot_response:
            print("❌ Помилка: Клієнт повторює бота! Генеруємо нову відповідь...")
            client_messages.pop()
            client_response = generate_ai_response(client_messages + dialogue_history)

        dialogue_history.append({"role": "user", "content": client_response})
        dialogue["dialogue"].append({"role": "client", "message": client_response})
        print(f"🧑‍💼 Клієнт: {client_response}\n")

    if len(dialogue["dialogue"]) < 2:
        print("❌ Помилка: Діалог не містить достатньо повідомлень!")
        return None

    return dialogue

def save_dialogues(dialogues, file_path):
    """Зберігає діалоги у JSON-файл."""
    if not dialogues:
        print("❌ Помилка: Список діалогів порожній, нічого зберігати.")
        return

    try:
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(dialogues, file, ensure_ascii=False, indent=4)
        print(f"\n✅ Діалоги збережено у {file_path}.")
    except Exception as e:
        print(f"❌ Помилка при збереженні файлу: {e}")

def main():
    """Генерує діалоги на основі промптів."""
    prompts = load_prompts(PROMPTS_FILE)
    bot_prompt = load_file(BOT_PROMPT_FILE)  # Завантажуємо промпт бота

    if not prompts or not bot_prompt:
        print("❌ Неможливо створити діалоги без промптів!")
        return

    dialogues = []
    for i, prompt in enumerate(prompts[:NUM_DIALOGUES]):
        print(f"\n🛠 Генерується діалог {i+1} для клієнта...")
        dialogue = create_dialogue(prompt, bot_prompt)
        if dialogue:
            dialogues.append(dialogue)

    print(f"\n🔍 Перевірка перед збереженням: {len(dialogues)} діалог(и) згенеровано.")
    save_dialogues(dialogues, DIALOGUES_FILE)

if __name__ == "__main__":
    main()