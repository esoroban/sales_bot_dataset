# generate_dialogues.py

import os
import json
import uuid
import openai
import random
import re

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Импортируем схемы, функции и генераторы JSON
from dialogue_functions import (
    stop_dialogue_schema,
    get_price_schema,
    sign_for_promo_schema,
    handle_ai_function_call,
    stop_dialogue,
    generate_get_price_json,
    generate_stop_dialogue_json,
    generate_sign_for_promo_json
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PROMPTS_FILE = os.path.join(DATA_DIR, "prompts.json")
DIALOGUES_FILE = os.path.join(DATA_DIR, "dialogues.json")
BOT_PROMPT_FILE = os.path.join(DATA_DIR, "bot_prompt.txt")

NUM_DIALOGUES = 10
NUM_EXCHANGES = 10

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

REFUSAL_KEYWORDS = [
    "не цікаво", "не потрібно", "відмовляюся", "не маю часу",
    "не планую", "не зацікавлена", "не підходить", "ні, дякую"
]

def is_goodbye(text: str) -> bool:
    txt_lower = text.lower()
    for pattern in GOODBYE_KEYWORDS:
        if re.search(pattern, txt_lower):
            return True
    return False

def is_price_inquiry(text: str) -> bool:
    return "кільки коштує" in text.lower()

def is_refusal(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in REFUSAL_KEYWORDS)

def check_success(text: str) -> bool:
    text = text.lower()
    return any(kw in text for kw in SUCCESS_KEYWORDS)

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

def generate_bot_response(bot_context, retry_count=0):
    """
    Генерує відповідь БОТА (assistant) з function calling.
    Если при запросе произошла ошибка — пробуем один раз повторить.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=bot_context,
            max_tokens=300,
            temperature=0.7,
            functions=[stop_dialogue_schema, get_price_schema, sign_for_promo_schema],
            function_call="auto"
        )
        return response
    except Exception as e:
        if retry_count < 1:
            return generate_bot_response(bot_context, retry_count=retry_count+1)
        print(f"❌ Ошибка генерации ответа бота: {e}")
        return None

def generate_client_response(client_context, retry_count=0):
    """
    Генерує відповідь КЛІЄНТА (assistant) без function calling.
    Если при запросе произошла ошибка — пробуем один раз повторить.
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
        if retry_count < 1:
            return generate_client_response(client_context, retry_count=retry_count+1)
        print(f"❌ Ошибка генерации ответа клиента: {e}")
        return None

def extract_bot_message_or_stop(response):
    """
    Повертає (bot_msg, stop_called).
    Якщо GPT викликала якусь function_call -> підміняємо bot_msg на текст із JSON.
    Якщо stop_dialogue -> stop_called = True (діалог завершується).
    Якщо get_price чи sign_for_promo -> stop_called = False.
    Якщо не було function_call -> bot_msg = звичайна відповідь бота, stop_called = False.
    """
    if not response or "choices" not in response:
        return None, False

    choice = response["choices"][0]
    msg = choice["message"]

    # Проверяем, вызвала ли GPT функцию
    if "function_call" in msg:
        func_call = msg["function_call"]
        name = func_call["name"]
        args_str = func_call.get("arguments") or "{}"
        args = json.loads(args_str)

        # Реально вызываем Python-функцию
        stop_called = handle_ai_function_call(choice)

        # Формируем текст, чтобы показать JSON-вызов в диалоге
        if name == "get_price":
            city = args.get("city", "Dnipro")
            online = args.get("online", False)
            bot_msg = f"Ось код виклику функції:\n```json\n{generate_get_price_json(city, online)}\n```"
            return bot_msg, stop_called

        elif name == "stop_dialogue":
            reason = args.get("reason", "")
            bot_msg = f"Ось код виклику функції:\n```json\n{generate_stop_dialogue_json(reason)}\n```"
            return bot_msg, stop_called

        elif name == "sign_for_promo":
            city = args.get("city", "Dnipro")
            child_name = args.get("child_name", "Нонейм")
            phone = args.get("phone", "12345678")
            bot_msg = f"Ось код виклику функції:\n```json\n{generate_sign_for_promo_json(city, child_name, phone)}\n```"
            return bot_msg, stop_called

        return "", stop_called

    # Если это обычный текст
    bot_msg = msg.get("content", "")
    return bot_msg.strip(), False

def extract_client_message(response):
    """
    Витягаємо текст із відповіді КЛІЄНТА (assistant).
    """
    if not response or "choices" not in response:
        return None
    choice = response["choices"][0]
    return choice["message"].get("content", "").strip()

def create_dialogue(prompt, bot_prompt):
    conversation_id = str(uuid.uuid4())
    dialogue = {"conversation_id": conversation_id, "dialogue": []}
    success = False
    refusal_count = 0
    dialogue_ended = False

    bot_context = [{"role": "system", "content": bot_prompt}]
    client_system = f"Ти — звичайний клієнт. Ось твій опис: {prompt['text']}"
    client_context = [{"role": "system", "content": client_system}]

    # Перше повідомлення бота
    greet = "Вітаю! Я – Штучний інтелект школи усного рахунку «Соробан». Чи є у вас хвилинка поспілкуватися?"
    bot_context.append({"role": "assistant", "content": greet})
    dialogue["dialogue"].append({"role": "sales_bot", "message": greet})

    # Перша відповідь клієнта
    client_context.append({"role": "user", "content": greet})
    resp_client = generate_client_response(client_context)
    if not resp_client:
        return dialogue, success

    client_msg = extract_client_message(resp_client) or ""
    dialogue["dialogue"].append({"role": "client", "message": client_msg})

    # Проверка на запрос цены
    if is_price_inquiry(client_msg):
        # Пример ручного вызова get_price
        handle_ai_function_call({
            "message": {
                "function_call": {
                    "name": "get_price",
                    "arguments": '{"city":"Dnipro","online":false}'
                }
            }
        })

    client_context.append({"role": "assistant", "content": client_msg})
    bot_context.append({"role": "user", "content": client_msg})

    # Проверка на прощание
    if is_goodbye(client_msg):
        final_bot = "Дякую, успіхів і до побачення!"
        dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
        stop_dialogue("клієнт одразу сказав «до побачення»")
        dialogue_ended = True
        return dialogue, success

    # Проверка на успех
    if check_success(client_msg):
        # Клиент сразу согласился
        success = True
        final_bot = "Чудово! Записую вас. Дякую за довіру, до зустрічі!"
        dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
        # Вызов sign_for_promo
        handle_ai_function_call({
            "message": {
                "function_call": {
                    "name": "sign_for_promo",
                    "arguments": '{"city":"Dnipro","child_name":"Нонейм","phone":"12345678"}'
                }
            }
        })
        stop_dialogue("успіх з першої ж репліки")
        dialogue_ended = True
        return dialogue, success
    else:
        if is_refusal(client_msg):
            refusal_count += 1

    # Основний цикл
    for step in range(NUM_EXCHANGES):
        if dialogue_ended:
            break

        # Ответ бота
        resp_bot = generate_bot_response(bot_context)
        if not resp_bot:
            break

        bot_msg, stop_called = extract_bot_message_or_stop(resp_bot)
        if bot_msg is None:
            break

        if bot_msg.strip() != "":
            dialogue["dialogue"].append({"role": "sales_bot", "message": bot_msg})

        if stop_called:
            dialogue_ended = True
            break

        if is_goodbye(bot_msg):
            stop_dialogue("бот сказав до побачення")
            dialogue_ended = True
            break

        bot_context.append({"role": "assistant", "content": bot_msg})
        client_context.append({"role": "user", "content": bot_msg})

        # Ответ клиента
        resp_client = generate_client_response(client_context)
        if not resp_client:
            break

        client_reply = extract_client_message(resp_client) or ""
        dialogue["dialogue"].append({"role": "client", "message": client_reply})

        # Проверка на запрос цены
        if is_price_inquiry(client_reply):
            handle_ai_function_call({
                "message": {
                    "function_call": {
                        "name": "get_price",
                        "arguments": '{"city":"Dnipro","online":false}'
                    }
                }
            })

        client_context.append({"role": "assistant", "content": client_reply})
        bot_context.append({"role": "user", "content": client_reply})

        if is_goodbye(client_reply):
            final_bot = "Дякую, успіхів і до побачення!"
            dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
            stop_dialogue("клієнт сказав до побачення")
            dialogue_ended = True
            break

        if check_success(client_reply):
            success = True
            final_bot = "Чудово, тоді оформимо запис! Дякую за вибір нашого курсу. До зустрічі!"
            dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
            # Вызов sign_for_promo
            handle_ai_function_call({
                "message": {
                    "function_call": {
                        "name": "sign_for_promo",
                        "arguments": '{"city":"Dnipro","child_name":"Нонейм","phone":"12345678"}'
                    }
                }
            })
            stop_dialogue("успіх")
            dialogue_ended = True
            break

        if is_refusal(client_reply):
            refusal_count += 1
            if refusal_count >= 2:
                final_bot = "Зрозуміло, дякую за ваш час! Якщо зміните думку, ми завжди на зв’язку. Успіхів!"
                dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
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