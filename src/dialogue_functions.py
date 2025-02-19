# dialogue_functions.py

import json

def stop_dialogue(reason: str):
    """
    Локальна Python-функція, яку GPT викликає, коли вирішує, 
    що діалог треба завершити (наприклад, після 2-ї відмови).
    """
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
            return True
        elif name == "price_info":
            price_info()
            # Після виклику price_info() діалог не обов’язково завершується.
            return False
    
    return False