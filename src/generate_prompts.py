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
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено: {file_path}")
        return {}
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not data:
        print(f"❌ Файл {file_path} пустий!")
    return data

def generate_prompts():
    persons = load_json(PERSONS_FILE)
    objections_map = load_json(OBJECTIONS_FILE)

    if not persons or not objections_map:
        print("❌ Неможливо створити промпти без даних!")
        return

    interest_levels = objections_map.get("interest_levels", {})
    reasons_map = objections_map.get("reasons", {})

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
        availability = person.get("availability", "невідомо")
        # Используем переименованное поле "желание записаться на курс"
        desire_value = str(person.get("желание записаться на курс", "0"))
        tone = person.get("tone", "Нейтральний")
        mood = person.get("mood", "Нейтральний")
        has_children = person.get("has_children", "немає")
        city = person.get("city", "невідомо")
        offline = person.get("offline", random.choice([True, False]))

        # Получаем фразы для уровня желания и причин отказа
        possible_phrases_interest = interest_levels.get(desire_value, ["Не маю коментарів."])
        chosen_interest_text = random.choice(possible_phrases_interest)

        if has_children == "немає":
            reason_key = "no_children"
            child_line = "У тебе немає дітей."
        else:
            reason_key = random.choice(all_reason_keys) if all_reason_keys else None
            child_line = f"У тебе є діти: {has_children}."

        if reason_key and reason_key in reasons_map:
            chosen_reason_phrases = reasons_map[reason_key]
            chosen_reason_text = random.choice(chosen_reason_phrases)
        else:
            chosen_reason_text = "Нема конкретної причини."

        short_response = random.choice(SHORT_RESPONSES)

        # Формируем не услужливый промпт
        personality_prompt = (
            f"Ти не бот, а реальна людина з міста {city}. Твоя відповідь завжди одне речення і без зайвих люб'язностей. "
            f"Твій стиль: {tone.lower()}. Твій настрій: {mood.lower()}. Рівень бажання записатися на курс: {desire_value}.\n"
            "Ти сумніваєшся в ефективності курсів і не любиш, коли щось нав’язують. Якщо тобі щось не до вподоби, кажеш прямо: "
            "«Не бачу сенсу» або «Мене це дратує».\n"
            "Скептично ставишся до нових пропозицій і не розповідаєш про нецікаві речі. "
            "Якщо питають: «Передайте знайомим?» — відповідаєш: «Я не хочу бути рекламним агентом чужих курсів». \n"
            "Якщо тобі зовсім не цікаво, розмову завершиш різко, без ввічливих формулювань.\n"
            "Щодо формату навчання: "
            f"{'Якби колись і займався, то виключно офлайн.' if offline else 'Якби колись і займався, то виключно онлайн.'}\n"
            "При відмові можеш використовувати такі фрази:\n"
            "– «Я звик самостійно опановувати потрібне, тут це зайве.»\n"
            "– «Не люблю витрачати час на подібні речі.»\n"
            "– «У мене обмаль часу, тож не хочу далі це обговорювати.»\n"
            "– «Не бачу сенсу рекомендувати знайомим те, що мені байдуже.»\n"
        )

        intro_line = f"Тебе звати {name}, тобі {age} років, ти живеш у місті {city}."
        prof_line = f"Ти {profession}, твоє хобі: {hobbies}."
        char_line = f"Твій характер: {character.lower()}."
        avail_line = f"Зараз ти {availability.lower()}."

        prompt_text = "\n".join([
            personality_prompt,
            intro_line,
            child_line,
            prof_line,
            char_line,
            avail_line,
            f"Початкова типова відповідь: «{short_response}»",
            f"При відмові зазвичай кажеш (бажання {desire_value}): «{chosen_interest_text}»",
            f"Причина відмови (reason={reason_key}): «{chosen_reason_text}»"
        ])

        prompts.append({
            "id": name,
            "text": prompt_text.strip()
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=4)

    print(f"\n✅ Збережено {len(prompts)} промптів у {OUTPUT_FILE}!")

if __name__ == "__main__":
    generate_prompts()