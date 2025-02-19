# dialogue_functions.py

import json

_dialogue_stopped = False  # Глобальний (чи модульний) прапорець, щоб уникнути дубльованих викликів

def stop_dialogue(reason: str):
    """
    Локальна Python-функція, яку GPT викликає, коли вирішує,
    що діалог треба завершити (наприклад, після 2-ї відмови).
    Якщо вже викликалась, вдруге не виводить дублюючих повідомлень.
    """
    global _dialogue_stopped
    if _dialogue_stopped:
        # Якщо вже був виклик, нічого не робимо
        return
    _dialogue_stopped = True
    print(f"🛑 stop_dialogue викликано з причиною: {reason}\n")


stop_dialogue_schema = {
    "name": "stop_dialogue",
    "description": "Завершує поточний діалог. Пояснює, чому діалог зупиняється.",
    "parameters": {
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "Причина завершення (напр. 'друга відмова' або 'немає інтересу')"
            }
        },
        "required": ["reason"]
    }
}

def price_info():
    """
    Функція, яку GPT викликає для повернення вартості курсу.
    (Вся логіка лише тут, без дублювань у тексті бота.)
    """
    print("💰 Ціна за курс: 2000 грн на місяць.")

price_info_schema = {
    "name": "price_info",
    "description": "Повертає вартість занять: 2000 грн на місяць",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}


def handle_ai_function_call(choice):
    """
    Перевіряє, чи GPT викликала stop_dialogue(reason) або price_info().
    Виконує відповідну функцію та повертає:
      - True, якщо це був stop_dialogue (і діалог треба завершити),
      - False, якщо це був price_info (або інша функція) і діалог триває.

    Завдяки _dialogue_stopped у stop_dialogue
    уникаємо повторних повідомлень у консолі.
    """
    if "message" not in choice:
        return False
    msg = choice["message"]
    if "function_call" in msg:
        func_call = msg["function_call"]
        name = func_call["name"]
        args_str = func_call.get("arguments") or "{}"
        args = json.loads(args_str)

        if name == "stop_dialogue":
            reason = args.get("reason", "")
            stop_dialogue(reason)
            return True  # сигналізуємо, що діалог треба завершити
        elif name == "price_info":
            price_info()
            # не завершуємо діалог
            return False

    return False