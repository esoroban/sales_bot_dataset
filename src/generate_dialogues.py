import os
import json
import uuid
import openai
import random
import re

from dialogue_functions import stop_dialogue_schema, handle_ai_function_call, stop_dialogue

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PROMPTS_FILE = os.path.join(DATA_DIR, "refined_prompts.json")
DIALOGUES_FILE = os.path.join(DATA_DIR, "dialogues.json")
BOT_PROMPT_FILE = os.path.join(DATA_DIR, "bot_prompt.txt")

NUM_DIALOGUES = 10
NUM_EXCHANGES = 10

NO_INTEREST_RESPONSES = [
    "Мені це не потрібно.",
    "Не цікаво.",
    "У мене інші плани.",
    "Я не думаю, що це корисно.",
    "Я не шукаю подібного."
]

SUCCESS_KEYWORDS = [
    "запишіть", "як записатися", "як можна записатися", "пробний урок",
    "хочу спробувати", "давайте спробуємо", "я згоден", "я згідна",
    "так, хочу", "так, згоден", "так, згодна"
]

# Ключові слова, що вказують на «прощання».
GOODBYE_KEYWORDS = [
    r"\bдо\s+побачення\b",
    r"\bдо\s+зустрічі\b",
    r"\bпрощавай\b",
    r"\bбувай\b"
]

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def is_goodbye(text: str) -> bool:
    """Перевіряє, чи містить текст ключові слова прощання (до побачення, до зустрічі)."""
    txt_lower = text.lower()
    for pattern in GOODBYE_KEYWORDS:
        if re.search(pattern, txt_lower):
            return True
    return False

def load_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено!")
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def load_prompts(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено!")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        print("❌ Файл промптів порожній!")
    return data

def generate_bot_response(bot_context):
    """
    Генерує відповідь БОТА (assistant) з function calling (stop_dialogue).
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=bot_context,
            max_tokens=300,
            temperature=0.7,
            functions=[stop_dialogue_schema],
            function_call="auto"
        )
        return response
    except Exception as e:
        print(f"❌ Помилка генерації відповіді бота: {e}")
        return None

def generate_client_response(client_context):
    """
    Генерує відповідь КЛІЄНТА (assistant) без function calling.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=client_context,
            max_tokens=300,
            temperature=0.7
        )
        return response
    except Exception as e:
        print(f"❌ Помилка генерації відповіді клієнта: {e}")
        return None

def extract_bot_message_or_stop(response):
    """
    Повертає (bot_msg, stop_called).
    Якщо модель викликала stop_dialogue, handle_ai_function_call(choice) -> True.
    """
    if not response or "choices" not in response:
        return None, False
    choice = response["choices"][0]

    # Перевіримо function_call
    if handle_ai_function_call(choice):
        return None, True

    bot_msg = choice["message"].get("content", "")
    return bot_msg.strip(), False

def extract_client_message(response):
    """
    Витягаємо текст із відповіді клієнта (assistant).
    """
    if not response or "choices" not in response:
        return None
    choice = response["choices"][0]
    return choice["message"].get("content", "").strip()

def check_success(client_msg: str) -> bool:
    """
    Перевіряє, чи містить репліка клієнта
    ключові слова, що вказують на бажання записатися.
    """
    text = client_msg.lower()
    return any(kw in text for kw in SUCCESS_KEYWORDS)

def is_refusal(msg: str) -> bool:
    """
    Перевірка на «відмову» за ключовими словами.
    """
    refusal_keywords = [
        "не цікаво", "не потрібно", "відмовляюся", "не маю часу",
        "не планую", "не зацікавлена", "не підходить", "ні, дякую"
    ]
    low = msg.lower()
    return any(kw in low for kw in refusal_keywords)

def create_dialogue(prompt, bot_prompt):
    conversation_id = str(uuid.uuid4())
    dialogue = {
        "conversation_id": conversation_id,
        "dialogue": []
    }

    success = False  # Чи вийшло «продати» курс
    refusal_count = 0

    bot_context = [
        {"role": "system", "content": bot_prompt}
    ]

    client_system = f"Ти — звичайний клієнт. Ось твій опис: {prompt['text']}"
    client_context = [
        {"role": "system", "content": client_system}
    ]

    # 1. Перше повідомлення бота
    greet = "Вітаю! Чи цікаво дізнатися про наші курси математики для дітей 5–12 років?"
    bot_context.append({"role": "assistant", "content": greet})
    dialogue["dialogue"].append({"role": "sales_bot", "message": greet})
    print(f"[БОТ]: {greet}")

    # 2. Перша відповідь клієнта
    client_context.append({"role": "user", "content": greet})
    resp_client = generate_client_response(client_context)
    if not resp_client:
        return dialogue, success
    
    client_msg = extract_client_message(resp_client) or ""
    dialogue["dialogue"].append({"role": "client", "message": client_msg})
    print(f"[КЛІЄНТ]: {client_msg}\n")

    client_context.append({"role": "assistant", "content": client_msg})
    bot_context.append({"role": "user", "content": client_msg})

    # Перевіряємо на «прощання» з боку клієнта
    if is_goodbye(client_msg):
        # Клієнт уже попрощався
        final_bot = "Дякую, успіхів і до побачення!"
        dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
        print(f"[БОТ]: {final_bot}\n")
        stop_dialogue("клієнт одразу сказав «до побачення»")
        return dialogue, success

    # Перевіряємо на успіх чи відмову
    if check_success(client_msg):
        success = True
        final_bot = "Чудово! Записую вас. Дякую за довіру, до зустрічі!"
        dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
        print(f"[БОТ]: {final_bot}\n")
        stop_dialogue("успіх з першої ж репліки")
        return dialogue, success
    else:
        if is_refusal(client_msg):
            refusal_count += 1

    # Основний цикл
    for step in range(NUM_EXCHANGES):
        # 1. Бот відповідає
        resp_bot = generate_bot_response(bot_context)
        if not resp_bot:
            break
        bot_msg, stop_called = extract_bot_message_or_stop(resp_bot)
        if stop_called:
            break
        if not bot_msg:
            break

        dialogue["dialogue"].append({"role": "sales_bot", "message": bot_msg})
        print(f"[БОТ]: {bot_msg}\n")

        # Якщо бот сам попрощався
        if is_goodbye(bot_msg):
            stop_dialogue("бот сказав до побачення")
            break

        bot_context.append({"role": "assistant", "content": bot_msg})
        client_context.append({"role": "user", "content": bot_msg})

        # 2. Клієнт відповідає
        resp_client = generate_client_response(client_context)
        if not resp_client:
            break
        client_reply = extract_client_message(resp_client) or ""
        dialogue["dialogue"].append({"role": "client", "message": client_reply})
        print(f"[КЛІЄНТ]: {client_reply}\n")

        client_context.append({"role": "assistant", "content": client_reply})
        bot_context.append({"role": "user", "content": client_reply})

        # Якщо клієнт попрощався
        if is_goodbye(client_reply):
            final_bot = "Дякую, успіхів і до побачення!"
            dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
            print(f"[БОТ]: {final_bot}\n")
            stop_dialogue("клієнт сказав до побачення")
            break

        # Перевірка успіху
        if check_success(client_reply):
            success = True
            final_bot = "Чудово, тоді оформимо запис! Дякую за вибір нашого курсу. До зустрічі!"
            dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
            print(f"[БОТ]: {final_bot}\n")
            stop_dialogue("успіх")
            break

        # Перевірка відмови
        if is_refusal(client_reply):
            refusal_count += 1
            if refusal_count >= 2:
                final_bot = "Зрозуміло, дякую за ваш час! Успіхів і всього найкращого!"
                dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
                print(f"[БОТ]: {final_bot}\n")
                handle_ai_function_call({
                    "message": {
                        "function_call": {
                            "name": "stop_dialogue",
                            "arguments": '{"reason":"друга відмова"}'
                        }
                    }
                })
                break

    return dialogue, success

def save_dialogues(dialogues, file_path):
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
        print("❌ Немає даних!")
        return

    dialogues = []
    success_count = 0

    for i, prompt in enumerate(prompts[:NUM_DIALOGUES]):
        print(f"\n🛠 Генерується діалог {i+1} для '{prompt['id']}'...\n")
        d, success = create_dialogue(prompt, bot_prompt)
        if d:
            dialogues.append(d)
            if success:
                success_count += 1

    save_dialogues(dialogues, DIALOGUES_FILE)

    print(f"\nЗагальна кількість діалогів: {len(dialogues)}")
    print(f"Успішних діалогів (запис на курс): {success_count}")

if __name__ == "__main__":
    main()