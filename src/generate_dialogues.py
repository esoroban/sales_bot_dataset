import os
import json
import uuid
import openai
import random

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

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    Генерує відповідь БОТА (assistant) з function calling.
    Використовує gpt-4o, але припускаємо, що у вас є адаптована версія
    з підтримкою function calling (за вашими словами).
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=bot_context,
            max_tokens=300,
            temperature=0.7,
            functions=[stop_dialogue_schema],
            function_call="auto"  # Дозволяємо GPT вирішувати
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
    Аналізуємо респонс від бота.
    Якщо викликана stop_dialogue -> handle_ai_function_call(choice) повертає True,
    тоді (None, True). Інакше (bot_text, False).
    """
    if not response or "choices" not in response:
        return None, False
    choice = response["choices"][0]

    # Якщо модель викликала функцію stop_dialogue
    if handle_ai_function_call(choice):
        return None, True

    # Інакше повертаємо текст
    bot_msg = choice["message"].get("content", "")
    return bot_msg.strip(), False

def extract_client_message(response):
    """
    Витягаємо текст із відповіді клієнта (assistant, без function_call).
    """
    if not response or "choices" not in response:
        return None
    choice = response["choices"][0]
    return choice["message"].get("content", "").strip()

def create_dialogue(prompt, bot_prompt):
    conversation_id = str(uuid.uuid4())
    dialogue = {
        "conversation_id": conversation_id,
        "dialogue": []
    }

    # Перевіримо, чи є "немає інтересу"
    interest_level = "слабкий інтерес"
    if "немає інтересу" in prompt["text"]:
        interest_level = "немає інтересу"

    bot_context = [
        {"role": "system", "content": bot_prompt}
    ]
    client_system = f"""
Ти — звичайний клієнт, не пропонуєш зустрічну допомогу.
Ось твій опис: {prompt["text"]}
"""
    client_context = [
        {"role": "system", "content": client_system}
    ]

    # Перше повідомлення бота
    greet = "Вітаю! Чи цікаво дізнатися про наші курси математики для дітей 5–12 років?"
    bot_context.append({"role": "assistant", "content": greet})
    dialogue["dialogue"].append({"role": "sales_bot", "message": greet})
    print(f"[БОТ]: {greet}")

    # Клієнт
    client_context.append({"role": "user", "content": greet})
    resp_client = generate_client_response(client_context)
    if not resp_client:
        return None
    client_msg = extract_client_message(resp_client)
    if not client_msg:
        return None

    dialogue["dialogue"].append({"role": "client", "message": client_msg})
    print(f"[КЛІЄНТ]: {client_msg}")

    client_context.append({"role": "assistant", "content": client_msg})
    bot_context.append({"role": "user", "content": client_msg})

    refusal_count = 0

    for step in range(NUM_EXCHANGES):
        # Якщо "немає інтересу" - завершуємо одразу
        if interest_level == "немає інтересу":
            denial = random.choice(NO_INTEREST_RESPONSES)
            dialogue["dialogue"].append({"role": "client", "message": denial})
            print(f"[КЛІЄНТ]: {denial} (немає інтересу)\n")
            # Бот каже останню фразу, викликає stop_dialogue
            final_bot = "Зрозуміло, тоді успіхів! До побачення."
            dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
            print(f"[БОТ]: {final_bot}\n")
            stop_dialogue("немає інтересу - завершення")
            break

        # 1. Бот
        resp_bot = generate_bot_response(bot_context)
        if not resp_bot:
            break
        bot_msg, stop_called = extract_bot_message_or_stop(resp_bot)
        if stop_called:
            # функція stop_dialogue викликана
            break
        if not bot_msg:
            break

        dialogue["dialogue"].append({"role": "sales_bot", "message": bot_msg})
        print(f"[БОТ]: {bot_msg}")

        bot_context.append({"role": "assistant", "content": bot_msg})
        client_context.append({"role": "user", "content": bot_msg})

        # 2. Клієнт
        resp_client = generate_client_response(client_context)
        if not resp_client:
            break
        client_reply = extract_client_message(resp_client)
        if not client_reply:
            break

        # Перевірка на відмову
        low = client_reply.lower()
        refusal_keywords = ["не цікаво", "не потрібно", "відмовляюся", "не маю часу",
                            "не планую", "не зацікавлена", "не підходить", "ні, дякую"]
        if any(kw in low for kw in refusal_keywords):
            refusal_count += 1

        dialogue["dialogue"].append({"role": "client", "message": client_reply})
        print(f"[КЛІЄНТ]: {client_reply}\n")

        client_context.append({"role": "assistant", "content": client_reply})
        bot_context.append({"role": "user", "content": client_reply})

        # Якщо 2 відмови - бот каже останнє слово -> виклик stop_dialogue
        if refusal_count >= 2:
            final_bot = "Зрозуміло, дякую за ваш час! Успіхів і всього найкращого!"
            dialogue["dialogue"].append({"role": "sales_bot", "message": final_bot})
            print(f"[БОТ]: {final_bot}\n")

            # Ініціюємо виклик
            # Імітуємо function_call stop_dialogue
            handle_ai_function_call({
                "message": {
                    "function_call": {
                        "name": "stop_dialogue",
                        "arguments": '{"reason":"друга відмова"}'
                    }
                }
            })
            break

    if len(dialogue["dialogue"]) < 2:
        print("❌ Надто короткий діалог.")
        return None

    return dialogue

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
    for i, prompt in enumerate(prompts[:NUM_DIALOGUES]):
        print(f"\n🛠 Генерується діалог {i+1} для '{prompt['id']}'...\n")
        d = create_dialogue(prompt, bot_prompt)
        if d:
            dialogues.append(d)

    save_dialogues(dialogues, DIALOGUES_FILE)

if __name__ == "__main__":
    main()