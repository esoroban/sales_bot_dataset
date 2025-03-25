#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import random
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PERSONS_FILE = os.path.join(DATA_DIR, "persons.json")
OBJECTIONS_FILE = os.path.join(DATA_DIR, "objections.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "prompts.json")

DEFAULT_NUM_PROMPTS = 10

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
        reasons_map[reason_key] = [
            phrase.replace("У тебе", "У мене")
                  .replace("Ти не", "Я не")
                  .replace("ти не", "я не")
            for phrase in reason_phrases
        ]

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_prompts():
    if len(sys.argv) > 1:
        try:
            num_prompts = int(sys.argv[1])
        except ValueError:
            print(f"Невірний аргумент, використовується значення за замовчуванням: {DEFAULT_NUM_PROMPTS}")
            num_prompts = DEFAULT_NUM_PROMPTS
    else:
        num_prompts = DEFAULT_NUM_PROMPTS

    persons = load_json(PERSONS_FILE)
    objections_map = load_json(OBJECTIONS_FILE)

    reasons_map = objections_map.get("reasons", {})
    rewrite_phrases(reasons_map)

    all_reason_keys = list(reasons_map.keys())
    if "no_children" in all_reason_keys:
        all_reason_keys.remove("no_children")

    prompts = []

    for person in persons[:num_prompts]:
        children = person.get("children", [])
        children_str = (
            f"У мене {len(children)} діточок: " + ", ".join(
                f"{ch['name']} ({ch['age']} років)" for ch in children
            ) + "."
            if children else "У мене немає дітей."
        )

        high_interest_line = ""
        sign_up_line = ""
        if person.get("interest", 0) >= 5:
            high_interest_line = (
                "Оскільки в мене досить високий інтерес, я можу поцікавитися ціною і погодитися на пробний урок.\n"
            )
            if any(5 <= ch["age"] <= 12 for ch in children):
                sign_up_line = (
                    "Якщо мене переконають у перевагах саме для дитини 5–12 років, можу записатися після уточнення ціни.\n"
                )

        chosen_reason_text = random.choice(
            reasons_map.get(random.choice(all_reason_keys), ["Нема конкретної причини."])
        )

        prompt_text = (
            "Ти не бот, а реальна людина. Говори лише від першої особи.\n"
            "Не використовуй другу особу (ти, твій, ваш) у відповідях.\n"
            "Не озвучуй ціни самостійно після викликів get_price(), лише сприймай інформацію від бота.\n"
            "Сприймай JSON-відповіді (get_price, запис на урок) як інформацію, а не як код.\n"
            f"Місто: {person['city']}, країна: {person['country']}.\n"
            f"Телефон: {person['phone']}.\n"
            f"Мене звати {person['name']}, мені {person['age']} років, працюю {person['profession']}.\n"
            f"Моє хобі: {person['hobbies']}.\n"
            f"Характер: {person['character']}.\n"
            f"{children_str}\n"
            f"Рівень інтересу: {INTEREST_STR_MAP[person['interest']]}.\n"
            f"Тон: {TONE_STR_MAP[person['tone']]}.\n"
            f"Настрій: {MOOD_STR_MAP[person['mood']]}.\n"
            "Відповідаю завжди одним реченням.\n"
            f"{high_interest_line}"
            f"{sign_up_line}"
            f"Початкова типова відповідь: «{random.choice(SHORT_RESPONSES)}»\n"
            f"Я сумніваюся і думаю, що: «{chosen_reason_text}»"
        )

        prompts.append({"id": person['name'], "text": prompt_text.strip()})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generate_prompts()