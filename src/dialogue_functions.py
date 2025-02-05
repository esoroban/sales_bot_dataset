import json

def stop_dialogue(reason: str):
    """
    Реальна Python-функція, яку GPT-4o викликає,
    коли вирішує, що діалог треба завершити.
    (Наприклад, після другої відмови від клієнта)
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

def handle_ai_function_call(choice):
    """
    Перевіряє, чи GPT викликала stop_dialogue(reason).
    Якщо так, викликає stop_dialogue(reason) локально
    і повертає True, аби головний цикл завершив діалог.
    Якщо ні, повертає False.
    """
    if "message" not in choice:
        return False
    msg = choice["message"]
    if "function_call" in msg:
        func_call = msg["function_call"]
        if func_call["name"] == "stop_dialogue":
            args = json.loads(func_call["arguments"])
            reason = args.get("reason", "")
            stop_dialogue(reason)
            return True
    return False