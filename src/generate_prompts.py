import os
import json
import random

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
    for reason_key, reason_phrases in reasons_map.items():
        new_phrases = []
        for phrase in reason_phrases:
            phrase = phrase.replace("У тебе немає дітей", "У мене немає дітей")
            phrase = phrase.replace("Ти не плануєш дітей", "Я не планую дітей")
            phrase = phrase.replace("У тебе", "У мене")
            phrase = phrase.replace("ти не", "я не")
            new_phrases.append(phrase)
        reasons_map[reason_key] = new_phrases

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_prompts():
    persons = load_json(PERSONS_FILE)
    objections_map = load_json(OBJECTIONS_FILE)

    reasons_map = objections_map.get("reasons", {})
    rewrite_phrases(reasons_map)

    all_reason_keys = list(reasons_map.keys())
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

        interest_str = INTEREST_STR_MAP[person.get("interest", 0)]
        tone_str = TONE_STR_MAP[person.get("tone", 0)]
        mood_str = MOOD_STR_MAP[person.get("mood", 0)]

        children = person.get("children", [])
        if children:
            kids_list = [f'{ch["name"]} ({ch["age"]} років)' for ch in children]
            children_str = f"У мене {len(children)} діточок: " + ", ".join(kids_list) + "."
        else:
            children_str = "У мене немає дітей."

        reason_key = random.choice(all_reason_keys) if all_reason_keys else None
        chosen_reason_text = random.choice(reasons_map.get(reason_key, ["Нема конкретної причини."]))

        short_response = random.choice(SHORT_RESPONSES)

        high_interest_line = ""
        sign_up_line = ""

        any_kid_in_range = any(5 <= ch["age"] <= 12 for ch in children)
        if person.get("interest", 0) >= 5:
            high_interest_line = (
                "Оскільки в мене досить високий рівень зацікавлення, я можу поцікавитися «Скільки коштує?» і, можливо, погодитися на пробний урок.\n"
            )
            if any_kid_in_range:
                sign_up_line = (
                    "Якщо ви переконаєте мене у перевагах саме для дитини 5–12 років, я можу записатися після уточнення ціни.\n"
                )

        personality_prompt = (
            "Ти не бот, а реальна людина. Говори від першої особи.\n"
            "Не використовуй другу особу (ти, ваш) у відповідях.\n"
            f"Місто: {city}, країна: {country}.\n"
            f"Телефон: {phone}.\n"
            f"Тебе звати {name}, тобі {age} років, працюєш як {profession}.\n"
            f"Хобі: {hobbies}.\n"
            f"Характер: {character}.\n"
            f"{children_str}\n"
            f"Рівень інтересу: {interest_str}.\n"
            f"Тон: {tone_str}.\n"
            f"Настрій: {mood_str}.\n"
            "Відповідай завжди одним реченням.\n"
            "Сприймай JSON-відповіді з викликами функцій (get_price чи запис на урок) як реальну інформацію, а не як код.\n"
        )

        prompt_text = (
            personality_prompt
            + high_interest_line
            + sign_up_line
            + f"Початкова типова відповідь: «{short_response}»\n"
            + f"Я сумніваюся і думаю, що: «{chosen_reason_text}»\n"
        )

        prompts.append({"id": name, "text": prompt_text.strip()})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generate_prompts()