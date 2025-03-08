import os
import json
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PERSONS_FILE = os.path.join(DATA_DIR, "persons.json")
OBJECTIONS_FILE = os.path.join(DATA_DIR, "objections.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "prompts.json")

NUM_PROMPTS = 10

TONE_DESCRIPTIONS = [
    "Грубий і неприємний",
    "Різкий",
    "Холодний",
    "Нейтральний",
    "Стримано-доброзичливий",
    "Помірно теплий",
    "Привітний",
    "Дружній",
    "М'який і уважний",
    "Максимально ввічливий та доброзичливий"
]

MOOD_DESCRIPTIONS = [
    "Дуже поганий настрій",
    "Роздратований",
    "Незадоволений",
    "Скептичний",
    "Нейтральний",
    "Помірно позитивний",
    "Гарний настрій",
    "Оптимістичний",
    "Радісний",
    "Енергійний і дуже доброзичливий"
]

def rewrite_phrases(reasons_map):
    """
    Переписываем «У тебе немає дітей» -> «У мене немає дітей»
    и «Ти не плануєш дітей» -> «Я не планую дітей» в файле возражений.
    """
    for reason_key, reason_phrases in reasons_map.items():
        new_list = []
        for phrase in reason_phrases:
            phrase = phrase.replace("У тебе немає дітей", "У мене немає дітей")
            phrase = phrase.replace("Ти не плануєш дітей", "Я не планую дітей")
            new_list.append(phrase)
        reasons_map[reason_key] = new_list

def load_json(file_path):
    """Загружает JSON-данные из указанного файла."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено: {file_path}")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        print(f"❌ Файл {file_path} порожній!")
    return data

def pick_initial_reply_by_mood(mood_num: int) -> str:
    """
    Возвращает начальную (типовую) реплику в зависимости от настроения:
      mood 0..2 -> максимально грубо,
      mood 3..6 -> более-менее нейтрально,
      mood 7..9 -> дружелюбно.
    """
    if mood_num <= 2:
        return "Нема часу. Коротше, що ти хочеш?"
    elif mood_num <= 6:
        return "Так, кажи."
    else:
        return "Вітаю! Чим можу допомогти?"

def pick_reason_phrase(reason_phrases, interest_num):
    """
    Возвращаем возражение из списка reason_phrases
    в зависимости от уровня интереса:
      - при interest 0..2 (низкий) берем начало списка (более грубые),
      - при interest 3..5 (средний) берем середину,
      - при interest 6..9 (высокий) берем конец списка (самые мягкие).
    Для упрощения делим список на 3 примерно равные части.
    """
    n = len(reason_phrases)
    if n == 0:
        return "Нема конкретної причини."

    # Разбиваем на три части
    # например, грубые ~ 0..(n//3), средние ~ (n//3)..(2*n//3), мягкие ~ (2*n//3)..n
    third = n // 3 if n > 2 else 1
    two_thirds = 2 * (n // 3)

    if interest_num <= 2:
        # Низкий интерес: берем начало списка
        subset = reason_phrases[0:third] if third > 0 else reason_phrases
    elif interest_num <= 5:
        # Средний: середина
        if third < two_thirds:
            subset = reason_phrases[third:two_thirds]
        else:
            subset = reason_phrases  # если мало элементов
    else:
        # Высокий: берем конец
        subset = reason_phrases[two_thirds:] if two_thirds < n else reason_phrases

    if len(subset) == 0:
        subset = reason_phrases  # fallback

    return random.choice(subset)

def generate_prompts():
    persons = load_json(PERSONS_FILE)
    objections_data = load_json(OBJECTIONS_FILE)
    if not persons or not objections_data:
        print("❌ Немає даних для генерації промптів!")
        return

    # Фразы для interest и reasons
    interest_levels_map = objections_data.get("interest_levels", {})
    reasons_map = objections_data.get("reasons", {})
    rewrite_phrases(reasons_map)

    all_reason_keys = list(reasons_map.keys())
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

        tone_num = person.get("tone", 0)
        mood_num = person.get("mood", 0)
        interest_num = person.get("interest", 0)

        # Получаем строку тона/настроения
        tone_str = TONE_DESCRIPTIONS[tone_num] if 0 <= tone_num < len(TONE_DESCRIPTIONS) else "Невідомий тон"
        mood_str = MOOD_DESCRIPTIONS[mood_num] if 0 <= mood_num < len(MOOD_DESCRIPTIONS) else "Невідомий настрій"

        children = person.get("children", [])
        children_count = len(children)

        # Выбираем причину
        if children_count == 0:
            reason_key = "no_children"
        else:
            reason_key = random.choice(all_reason_keys) if all_reason_keys else None

        if reason_key and reason_key in reasons_map:
            chosen_reason = pick_reason_phrase(reasons_map[reason_key], interest_num)
        else:
            chosen_reason = "Нема конкретної причини."

        # Формируем строку о детях
        if children_count > 0:
            kids_info = []
            for c in children:
                child_name = c.get("name", "Безіменний")
                child_age = c.get("age", 0)
                kids_info.append(f"{child_name} {child_age} років")
            kids_line = f"У тебе {children_count} дітей: " + ", ".join(kids_info) + "."
        else:
            kids_line = "У тебе немає дітей."

        # Интерес
        if str(interest_num) in interest_levels_map:
            interest_phrases = interest_levels_map[str(interest_num)]
            random_interest_phrase = random.choice(interest_phrases)
        else:
            random_interest_phrase = "Поки що не маєш чіткої позиції."

        # Дополнительные фразы при interest>5 и наличии ребёнка 5..12
        any_kid_in_range = any(5 <= c.get("age", 0) <= 12 for c in children)
        special_lines = []
        if interest_num > 5 and any_kid_in_range:
            special_lines.append("Якщо мені цікаво та хтось переконає мене, я б залюбки поцікавилась ціною.")
            if interest_num in [7, 8]:
                special_lines.append("Я не проти переконатися на промо якість уроку.")
            elif interest_num == 9:
                special_lines.append("Я бажаю дізнатися про методику і врешті записатися на промо-урок.")

        # Начальная реплика по настроению
        initial_reply = pick_initial_reply_by_mood(mood_num)

        # Собираем всё
        personality_prompt = (
            "Ти не бот, а реальна людина.\n\n"
            f"Твій стиль: {tone_str}.\n"
            f"Твій настрій: {mood_str}.\n\n"
            "Твоя відповідь завжди з одного речення."
        )

        intro_line = f"Тебе звати {name}, тобі {age} років, ти ведеш {lifestyle} спосіб життя."
        prof_line = f"Ти {profession}, твоє хобі — {hobbies}."
        char_line = f"Твій характер — {character.lower()}."

        extra_str = "\n".join(special_lines)

        prompt_text = "\n".join(filter(None, [
            personality_prompt,
            intro_line,
            prof_line,
            char_line,
            kids_line,
            f"Початкова типова відповідь: «{initial_reply}»",
            f"Ти сумніваєшся, і це викликано тим, що: «{random_interest_phrase}».",
            f"Якщо ти сумніваєшся, то це викликано: «{chosen_reason}».",
            extra_str
        ]))

        prompts.append({
            "id": name,
            "text": prompt_text
        })

    # Сохраняем
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Збережено {len(prompts)} промптів у {OUTPUT_FILE}!")


if __name__ == "__main__":
    generate_prompts()