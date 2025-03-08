# dialogue_functions.py

import json

_dialogue_stopped = False

def stop_dialogue(reason: str):
    global _dialogue_stopped
    if _dialogue_stopped:
        return
    _dialogue_stopped = True
    print(f"🛑 stop_dialogue викликано з причиною: {reason}\n")

stop_dialogue_schema = {
    "name": "stop_dialogue",
    "description": "Завершує поточний діалог...",
    "parameters": {
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "Причина..."
            }
        },
        "required": ["reason"]
    }
}

def get_price(city="Dnipro", online=False):
    print(f"Викликаємо розрахунок ціни для {city} (online={online}).")

get_price_schema = {
    "name": "get_price",
    "description": "Повертає вартість занять з урахуванням міста і формату (online чи офлайн).",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Місто (англійською)"
            },
            "online": {
                "type": "boolean",
                "description": "Чи онлайн формат"
            }
        },
        "required": ["city", "online"]
    }
}

def sign_for_promo(city="Dnipro", child_name="Нонейм", phone="12345678"):
    print(f"✍ Записуємо на промо: {city}, {child_name}, {phone}")

sign_for_promo_schema = {
    "name": "sign_for_promo",
    "description": "Записує на пробний урок.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "Місто"},
            "child_name": {"type": "string", "description": "Ім'я дитини"},
            "phone": {"type": "string", "description": "Телефон"}
        },
        "required": ["city", "child_name", "phone"]
    }
}

def generate_get_price_json(city="Dnipro", online=False):
    return json.dumps({
        "function_call": {
            "name": "get_price",
            "arguments": {
                "city": city,
                "online": online
            }
        }
    }, ensure_ascii=False)

def generate_stop_dialogue_json(reason="друга відмова"):
    return json.dumps({
        "function_call": {
            "name": "stop_dialogue",
            "arguments": {
                "reason": reason
            }
        }
    }, ensure_ascii=False)

def generate_sign_for_promo_json(city="Dnipro", child_name="Нонейм", phone="12345678"):
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
        elif name == "get_price":
            city = args.get("city", "Dnipro")
            online = args.get("online", False)
            get_price(city, online)
            return False
        elif name == "sign_for_promo":
            city = args.get("city", "Dnipro")
            child_name = args.get("child_name", "Нонейм")
            phone = args.get("phone", "12345678")
            sign_for_promo(city, child_name, phone)
            return False

    return False