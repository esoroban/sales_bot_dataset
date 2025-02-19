import os
import json
import uuid
import openai
import random
import re

# Імпортуємо схеми та функції з dialogue_functions
from dialogue_functions import (
    stop_dialogue_schema,
    price_info_schema,
    handle_ai_function_call,
    stop_dialogue
)

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
    """
    Перевіряє, чи містить текст ключові слова прощання 
    (наприклад, 'до побачення', 'до зустрічі').
    Повертає True, якщо знайшли збіг.
    """
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
    Генерує відповідь БОТА (assistant) з function calling:
    stop_dialogue або price_info.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=bot_context,
            max_tokens=300,
            temperature=0.7,
            functions=[stop_dialogue_schema, price_info_schema],
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

    Якщо GPT викликала stop_dialogue — stop_called = True, діалог завершуємо.
    Якщо GPT викликала price_info — stop_called = False, але bot_msg = "".

    Якщо не було function_call, bot_msg — текст відповіді бота.
    """
    if not response or "choices" not in response:
        return None, False
    choice = response["choices"][0]

    called_function = handle_ai_function_call(choice)
    if called_function:
        # Якщо це stop_dialogue, повертаємо True (діалог завершується).
        # Якщо price_info, це False (діалог триває), але bot_msg = "".
        return "", called_function

    bot_msg = choice["message"].get("content")
    if bot_msg is None:
        return "", False

    return bot_msg.strip(), False

def extract_client_message(response):
    """
    Витягаємо текст відповіді КЛІЄНТА (assistant role).
    """
    if not response or "choices" not in response:
        return None
    choice = response["choices"][0]
    return choice["message"].get("content", "").strip()

def check_success(client_msg: str) -> bool:
    """
    Перевіряє, чи містить репліка клієнта
    ключові слова, що означають згоду на запис (успіх).
    """
    text = client_msg.lower()
    return any(kw in text for kw in SUCCESS_KEYWORDS)

def is_refusal(msg: str) -> bool:
    """
    Перевіряє, чи містить репліка клієнта слова відмови.
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
    success = False
    refusal_count = 0
    dialogue_ended = False  # маркер, що діалог завершено

    bot_context = [
        {"role": "system", "content": bot_prompt}
    ]
    client_system = f"Ти — звичайний клієнт. Ось твій опис: {prompt['text']}"
    client_context = [
        {"role": "system", "content": client_system}
    ]

    # 1) Перше повідомлення бота
    greet = "Вітаю! Я – Штучний інтелект школи усного рахунку «Соробан». Чи є у вас хвилинка поспілкуватися?"
    bot_context.append({"role": "assistant", "content": greet})
    dialogue["dialogue"].append({"role": "sales_bot", "message": greet})
    print(f"[БОТ]: {greet}")

    # 2) Перша відповідь клієнта
    client_context.append({"role": "user", "content": greet})
    resp_client = generate_client_response(client_context)
    if not resp_client:
        return dialogue, success  # клієнт не згенерував відповіді

    client_msg = extract_client_message(resp_client) or ""
    dialogue["dialogue"].append({"role": "client", "message": client_msg})
    print(f"[КЛІЄНТ]: {client_msg}\n")

    # Примусово перевіряємо, чи не питає клієнт "Скільки коштує?"
    # Якщо так і GPT не викликала price_info, викликаємо самі:
    if "кільки коштує" in client_msg.lower():
        handle_ai_function_call({
            "message": {
                "function_call": {
                    "name": "price_info",
                    "arguments": "{}"
                }
            }
        })

    client_context.append({"role": "assistant", "content": client_msg})
    bot_context.append({"role": "user", "content": client_msg})

    # Перевірка прощання
    if is_goodbye(client_msg):
        final_bot = "Дякую, успіхів і до побачення!"
        dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
        print(f"[БОТ]: {final_bot}\n")
        stop_dialogue("клієнт одразу сказав «до побачення»")
        dialogue_ended = True
        return dialogue, success

    # Перевірка успіху
    if check_success(client_msg):
        success = True
        final_bot = "Чудово! Записую вас. Дякую за довіру, до зустрічі!"
        dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
        print(f"[БОТ]: {final_bot}\n")
        stop_dialogue("успіх з першої ж репліки")
        dialogue_ended = True
        return dialogue, success
    else:
        # Можливо, це перша відмова
        if is_refusal(client_msg):
            refusal_count += 1

    # Основний цикл діалогу
    for step in range(NUM_EXCHANGES):
        if dialogue_ended:
            break

        # 1) Відповідь бота
        resp_bot = generate_bot_response(bot_context)
        if not resp_bot:
            break

        bot_msg, stop_called = extract_bot_message_or_stop(resp_bot)
        # Якщо stop_called == True i це stop_dialogue, діалог завершується.
        # Якщо це price_info => продовжуємо, але bot_msg = ""
        if bot_msg is None:
            break

        if bot_msg == "" and stop_called is True:
            # Це був price_info, діалог триває
            # Продовжимо цикл без додавання репліки
            continue

        if bot_msg.strip() == "":
            # Порожня репліка
            continue

        # Додаємо репліку бота в діалог
        dialogue["dialogue"].append({"role": "sales_bot", "message": bot_msg})
        print(f"[БОТ]: {bot_msg}\n")

        # Якщо бот попрощався — діалог завершено
        if is_goodbye(bot_msg):
            stop_dialogue("бот сказав до побачення")
            dialogue_ended = True
            break

        # Додаємо репліку бота в контекст
        bot_context.append({"role": "assistant", "content": bot_msg})
        client_context.append({"role": "user", "content": bot_msg})

        # 2) Відповідь клієнта
        resp_client = generate_client_response(client_context)
        if not resp_client:
            break
        client_reply = extract_client_message(resp_client) or ""
        dialogue["dialogue"].append({"role": "client", "message": client_reply})
        print(f"[КЛІЄНТ]: {client_reply}\n")

        # Якщо клієнт знову питає "Скільки коштує?"
        if "кільки коштує" in client_reply.lower():
            handle_ai_function_call({
                "message": {
                    "function_call": {
                        "name": "price_info",
                        "arguments": "{}"
                    }
                }
            })

        client_context.append({"role": "assistant", "content": client_reply})
        bot_context.append({"role": "user", "content": client_reply})

        if is_goodbye(client_reply):
            final_bot = "Дякую, успіхів і до побачення!"
            dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
            print(f"[БОТ]: {final_bot}\n")
            stop_dialogue("клієнт сказав до побачення")
            dialogue_ended = True
            break

        if check_success(client_reply):
            success = True
            final_bot = "Чудово, тоді оформимо запис! Дякую за вибір нашого курсу. До зустрічі!"
            dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
            print(f"[БОТ]: {final_bot}\n")
            stop_dialogue("успіх")
            dialogue_ended = True
            break

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
                dialogue_ended = True
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