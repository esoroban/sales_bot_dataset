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

    interest_levels = objections_map.get("interest_levels", {})
    reasons_map = objections_map.get("reasons", {})

    # Усі можливі ключі з reasons (окрім "no_children", якщо треба пропускати його випадково).
    all_reason_keys = list(reasons_map.keys())
    # Припустимо, що "no_children" завжди призначається лише примусово, тому для рандому прибираємо:
    if "no_children" in all_reason_keys:
        all_reason_keys.remove("no_children")

    prompts = []

    for person in persons[:NUM_PROMPTS]:
        name = person.get("name", "Невідомий")
        age = person.get("age", 0)
        profession = person.get("profession", "безробітний")
        lifestyle = person.get("lifestyle", "міське")
        hobbies = person.get("hobbies", "не вказані")
        character = person.get("character", "невизначений")
        availability = person.get("availability", "невідомо")
        interest_value = str(person.get("interest", "0"))  # приводимо до string
        tone = person.get("tone", "Нейтральний")
        mood = person.get("mood", "Нейтральний")
        children_ages = person.get("children_ages", [])

        # 1. Визначаємо 'interest' (0–9)
        possible_phrases_interest = interest_levels.get(interest_value, ["Не маю коментарів."])
        chosen_interest_text = random.choice(possible_phrases_interest)

        # 2. Визначаємо 'reason'
        # Якщо немає дітей => reason = "no_children"
        # Якщо діти є => рандомно з інших reasons
        if not children_ages:
            reason_key = "no_children"
        else:
            # Вибираємо довільний ключ з all_reason_keys
            reason_key = random.choice(all_reason_keys) if all_reason_keys else None

        # Витягуємо масив фраз за reason_key
        if reason_key and reason_key in reasons_map:
            chosen_reason_phrases = reasons_map[reason_key]
            chosen_reason_text = random.choice(chosen_reason_phrases)
        else:
            chosen_reason_text = "Нема конкретної причини."

        # 3. Рандомне коротке різке «привітання / реакція»
        short_response = random.choice(SHORT_RESPONSES)

        # 4. Формуємо personality_prompt
        personality_prompt = (
            "Ти не бот, а реальна людина. Ти говориш завжди від першой особи. "
            "Ти не намагаєшся бути особливо ввічливим, говориш коротко й прямо. "
            "Часто використовуєш односкладні чи різкі відповіді, коли тебе щось не цікавить. "
            f"Типові початкові реакції можуть бути: {', '.join(SHORT_RESPONSES)}. "
            f"Твій стиль: {tone.lower()}. Твій настрій: {mood.lower()}. "
            f"Рівень зацікавлення: {interest_value}.\n"
            "Якщо курси тебе не цікавлять, можеш казати, наприклад:\n"
            "– «У мене вже є репетитор.»\n"
            "– «Дитина перевантажена секціями.»\n"
            "– «Ми пробували подібне, не зайшло.»\n"
            "– «Я не бачу сенсу в такому навчанні.»\n"
            "Якщо тобі щось не зрозуміло, ти можеш запитати:\n"
            "– «У чому суть?»\n"
            "– «Чим це кращe за інші курси?»\n"
            "– «Який графік занять?»\n"
            "– «Скільки коштує?»\n"
            "Коли бот питає про знайомих, логічно казати:\n"
            "– «Можливо, у когось із подруг є діти, але не пригадаю» або «Не знаю».\n"
        )

        # 5. Короткий вступ (ім'я, вік, стиль, діти, професія)
        intro_line = f"Тебе звати {name}, тобі {age} років, ти ведеш {lifestyle} спосіб життя."
        if children_ages:
            ages_str = ", ".join(map(str, children_ages))
            child_line = f"У тебе {len(children_ages)} діт{'и' if len(children_ages)>1 else 'ина'} ({ages_str} років)."
        else:
            child_line = "У тебе немає дітей."

        prof_line = f"Ти {profession}, твоє хобі: {hobbies}."
        char_line = f"Твій характер: {character.lower()}."
        avail_line = f"Зараз ти {availability.lower()}."

        # 6. Формуємо фінальний текст
        prompt_text = "\n".join([
            personality_prompt,
            intro_line,
            child_line,
            prof_line,
            char_line,
            avail_line,
            f"Початкова типова відповідь: «{short_response}»",
            f"При відмові зазвичай кажеш (interest {interest_value}): «{chosen_interest_text}»",
            f"Випадкова причина відмови (reason={reason_key}): «{chosen_reason_text}»"
        ])

        prompts.append({
            "id": name,
            "text": prompt_text.strip()
        })

    # Зберігаємо результат
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=4)

    print(f"\n✅ Збережено {len(prompts)} промптів у {OUTPUT_FILE}!")

if __name__ == "__main__":
    generate_prompts()