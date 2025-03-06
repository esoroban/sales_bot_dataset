import json

_dialogue_stopped = False  # Глобальний (чи модульний) прапорець, щоб уникнути дублюваних викликів

def stop_dialogue(reason: str):
    """
    Локальна Python-функція, яку GPT викликає, коли вирішує,
    що діалог треба завершити (наприклад, після 2-ї відмови).
    Якщо вже викликалась, вдруге не виводить дублюючих повідомлень.
    """
    global _dialogue_stopped
    if _dialogue_stopped:
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

def sign_for_promo(city="Dnipro", child_name="Нонейм", phone="12345678"):
    """
    Функція, яку GPT викликає для запису на пробний урок.
    """
    print(f"✍ Записуємо на промо: {city}, {child_name}, {phone}")

sign_for_promo_schema = {
    "name": "sign_for_promo",
    "description": "Записує на пробний урок.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Місто"
            },
            "child_name": {
                "type": "string",
                "description": "Ім'я дитини"
            },
            "phone": {
                "type": "string",
                "description": "Телефон"
            }
        },
        "required": ["city", "child_name", "phone"]
    }
}

def generate_price_info_json():
    """
    Повертає JSON, який показує виклик функції price_info().
    """
    return json.dumps({
        "function_call": {
            "name": "price_info",
            "arguments": {}
        }
    }, ensure_ascii=False)

def generate_stop_dialogue_json(reason="друга відмова"):
    """
    Повертає JSON, який показує виклик функції stop_dialogue(reason).
    """
    return json.dumps({
        "function_call": {
            "name": "stop_dialogue",
            "arguments": {
                "reason": reason
            }
        }
    }, ensure_ascii=False)

def generate_sign_for_promo_json(city="Dnipro", child_name="Нонейм", phone="12345678"):
    """
    Повертає JSON, який показує виклик функції sign_for_promo().
    """
    return json.dumps({
        "function_call": {
            "name": "sign_for_promo",
            "arguments": {
                "city": city,
                "child_name": child_name,
                "phone": phone
            }
        }
    }, ensure_ascii=False)

def handle_ai_function_call(choice):
    """
    Перевіряє, чи GPT викликала stop_dialogue(reason), price_info() або sign_for_promo().
    Виконує відповідну функцію та повертає:
      - True, якщо це був stop_dialogue (діалог треба завершити),
      - False, якщо це був price_info чи sign_for_promo (діалог триває).
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
            return False
        elif name == "sign_for_promo":
            city = args.get("city", "Dnipro")
            child_name = args.get("child_name", "Нонейм")
            phone = args.get("phone", "12345678")
            sign_for_promo(city, child_name, phone)
            return False

    return False