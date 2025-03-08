import os
import json
import random
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PERSONS_FILE = os.path.join(DATA_DIR, "persons.json")
OBJECTIONS_FILE = os.path.join(DATA_DIR, "objections.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "prompts.json")

NUM_PROMPTS = 10

SHORT_RESPONSES = [
    "Що саме?",
    "У чому суть?",
    "Навіщо це?",
    "Слухаю.",
    "Так, говоріть.",
    "Який сенс?",
    "Скільки коштує?",
    "Я зайнятий, кажіть швидко.",
    "Чим це кращe за інші курси?",
    "Нема часу. Коротше, що ви хочете?"
]

# Текстовые описания interest (0..9)
INTEREST_STR_MAP = {
    0: "Не цікаво зовсім",
    1: "Майже не цікаво",
    2: "Слабкий інтерес",
    3: "Низький інтерес",
    4: "Помірний інтерес",
    5: "Дещо цікаво",
    6: "Зацікавлений",
    7: "Досить цікавить",
    8: "Дуже цікаво",
    9: "Максимально зацікавлений"
}

# Текстовые описания тона (0..9)
TONE_STR_MAP = {
    0: "Грубий і неприємний",
    1: "Різкий",
    2: "Холодний",
    3: "Нейтральний",
    4: "Стримано-доброзичливий",
    5: "Помірно теплий",
    6: "Привітний",
    7: "Дружній",
    8: "М'який і уважний",
    9: "Максимально ввічливий та доброзичливий"
}

# Текстовые описания настроения (0..9)
MOOD_STR_MAP = {
    0: "Дуже поганий настрій",
    1: "Роздратований",
    2: "Незадоволений",
    3: "Скептичний",
    4: "Нейтральний",
    5: "Помірно позитивний",
    6: "Гарний настрій",
    7: "Оптимістичний",
    8: "Радісний",
    9: "Енергійний і дуже доброзичливий"
}

def rewrite_phrases(reasons_map):
    """
    Переписываем некоторые фразы, чтобы звучало от первого лица.
    """
    for reason_key, reason_phrases in reasons_map.items():
        new_phrases = []
        for phrase in reason_phrases:
            phrase = phrase.replace("У тебе немає дітей", "У мене немає дітей")
            phrase = phrase.replace("Ти не плануєш дітей", "Я не планую дітей")
            new_phrases.append(phrase)
        reasons_map[reason_key] = new_phrases

def load_json(file_path):
    """Завантажує дані з JSON-файлу."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено: {file_path}")
        return {}
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not data:
        print(f"❌ Файл {file_path} пустий!")
    return data

def generate_prompts():
    """Генерує ПРОМПТИ (опис клієнта) для використання в ІІ."""

    persons = load_json(PERSONS_FILE)
    objections_map = load_json(OBJECTIONS_FILE)

    if not persons or not objections_map:
        print("❌ Неможливо створити промпти без даних!")
        return

    # Переписываем нежелательные фразы
    reasons_map = objections_map.get("reasons", {})
    rewrite_phrases(reasons_map)
    objections_map["reasons"] = reasons_map

    all_reason_keys = list(reasons_map.keys())
    # Можно убрать "no_children" из рандома
    if "no_children" in all_reason_keys:
        all_reason_keys.remove("no_children")

    prompts = []

    for person in persons[:NUM_PROMPTS]:
        name = person.get("name", "Невідомий")
        age = person.get("age", 0)
        profession = person.get("profession", "безробітний")
        hobbies = person.get("hobbies", "не вказані")
        character = person.get("character", "невизначений")
        phone = person.get("phone", "0000000000")
        city = person.get("city", "Невідоме місто")
        country = person.get("country", "Невідома країна")

        # Интерес/тон/настрой (числа 0..9), мапим в строки
        interest_num = person.get("interest", 0)
        tone_num = person.get("tone", 0)
        mood_num = person.get("mood", 0)

        interest_str = INTEREST_STR_MAP.get(interest_num, "Невідомий інтерес")
        tone_str = TONE_STR_MAP.get(tone_num, "Невідомий тон")
        mood_str = MOOD_STR_MAP.get(mood_num, "Невідомий настрій")

        children = person.get("children", [])
        if children:
            kids_list = []
            for ch in children:
                ch_name = ch.get("name", "???")
                ch_age = ch.get("age", 0)
                kids_list.append(f"{ch_name} ({ch_age} років)")
            # Пример: "У мене 2 діточок: Соломія (9 років), Оля (15 років)."
            children_str = f"У мене {len(children)} діточок: " + ", ".join(kids_list) + "."
        else:
            children_str = "У мене немає дітей."

        # Выбираем случайную причину-возражение
        reason_key = random.choice(all_reason_keys) if all_reason_keys else None
        if reason_key and reason_key in reasons_map:
            chosen_reason_phrases = reasons_map[reason_key]
            chosen_reason_text = random.choice(chosen_reason_phrases)
        else:
            chosen_reason_text = "Нема конкретної причини."

        # Случайная короткая реакция
        short_response = random.choice(SHORT_RESPONSES)

        # Если интерес >= 5 — добавим строку о том, что можем спросить цену и согласиться
        high_interest_line = ""
        if interest_num >= 5:
            high_interest_line = (
                "Оскільки в мене досить високий рівень зацікавлення, "
                "я можу поцікавитися «Скільки коштує?» і, можливо, погодитися на пробний урок.\n"
            )

        # Если среди детей есть возраст 5..12 и интерес >=5 — доп. строка
        any_kid_in_range = any(5 <= ch.get("age", 0) <= 12 for ch in children)
        sign_up_line = ""
        if any_kid_in_range and interest_num >= 5:
            sign_up_line = (
                "Якщо ви переконаєте мене у перевагах саме для дитини 5–12 років, "
                "я можу записатися після уточнения ціни.\n"
            )

        # Формируем текст промпта
        personality_prompt = (
            "Ти не бот, а реальна людина. Ти говориш від першої особи, коротко й прямо.\n"
            f"Місто: {city}, країна: {country}.\n"
            f"Телефон: {phone}.\n"
            f"Тебе звати {name}, тобі {age} років, ти працюєш як {profession}.\n"
            f"Твоє хобі: {hobbies}.\n"
            f"Твій характер: {character}.\n"
            f"{children_str}\n"
            # Интерес/тон/настрой — строковые:
            f"Рівень інтересу: {interest_str}.\n"
            f"Тон: {tone_str}.\n"
            f"Настрій: {mood_str}.\n"
            "Твоя відповідь завжди з одного речення.\n"
        )

        prompt_text = (
            personality_prompt
            + high_interest_line
            + sign_up_line
            + f"Початкова типова відповідь: «{short_response}»\n"
            + f"Ти сумніваєшся і думаєш, що: «{chosen_reason_text}»\n"
        )

        prompts.append({
            "id": name,
            "text": prompt_text.strip()
        })

    # Сохраняем результат
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=4)

    print(f"\n✅ Збережено {len(prompts)} промптів у {OUTPUT_FILE}!")

if __name__ == "__main__":
    generate_prompts()