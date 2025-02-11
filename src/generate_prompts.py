import os
import json
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PERSONS_FILE = os.path.join(DATA_DIR, "persons.json")
OBJECTIONS_FILE = os.path.join(DATA_DIR, "objections.json")  # Новий файл із фразами
OUTPUT_FILE = os.path.join(DATA_DIR, "prompts.json")

NUM_PROMPTS = 10

def load_persons(file_path):
    """Завантажує список готових особистостей із JSON."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено! Спочатку запустіть generate_persons.py.")
        return []
    
    with open(file_path, "r", encoding="utf-8") as file:
        persons = json.load(file)
    
    if not persons:
        print("❌ Помилка: Файл персон порожній!")
    
    return persons

def load_objections(file_path):
    """Завантажує об’єкти (фрази) для кожного рівня інтересу з objections.json."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено! Створіть objections.json.")
        return {}
    
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    if not data:
        print("❌ Файл objections.json порожній!")
    
    return data

def generate_prompts():
    """
    Генерує “первинні” промпти клієнта, використовуючи:
      - person["interest_level"] (0..9)
      - Файл objections.json для вибору випадкової фрази (і відмови, і зацікавленості).
      - 3-4 речення опису: вік, професія, сім.стан, рівень інтересу...
    """

    persons = load_persons(PERSONS_FILE)
    objections_map = load_objections(OBJECTIONS_FILE)

    if not persons or not objections_map:
        print("❌ Неможливо створити промпти без даних!")
        return

    prompts = []

    for person in persons[:NUM_PROMPTS]:
        name = person.get("name", "Невідомий")
        age = person.get("age", 0)
        profession = person.get("profession", "безробітний")
        lifestyle = person.get("lifestyle", "міське")
        hobbies = person.get("hobbies", "не вказані")
        character = person.get("character", "невизначений")
        children_ages = person.get("children_ages", [])
        has_children = bool(children_ages)
        availability_info = person.get("availability", "невідомо")
        interest_level = person.get("interest_level", 0)  # 0..9

        # Сформуємо короткий опис
        # 1. Привітання та вік
        if age:
            line_intro = f"Мене звати {name}, мені {age} років, веду {lifestyle} спосіб життя."
        else:
            line_intro = f"Мене звати {name}, я живу в {lifestyle} місцевості."

        # 2. Діти
        if has_children:
            ages_str = ", ".join(map(str, children_ages))
            child_text = f"У мене {len(children_ages)} діт{'и' if len(children_ages)>1 else 'ина'} ({ages_str} років)."
        else:
            child_text = "У мене немає дітей."

        # 3. Професія + характер
        if character.lower() == "емпат":
            profession_line = (
                f"Я {profession}, люблю {hobbies}, і як емпат враховую почуття інших."
            )
        else:
            profession_line = (
                f"Я {profession}, люблю {hobbies}, і як {character} оцінюю все раціонально."
            )

        # 4. Визначимо «відмову/заперечення» або «зацікавленість», базуючись на interest_level
        # Перетворимо interest_level в стрічку "0"..."9"
        interest_str = str(interest_level)
        possible_objections = objections_map.get(interest_str, ["Не можу зараз нічого сказати."])
        # Випадкова фраза згідно рівня інтересу
        chosen_objection = random.choice(possible_objections)

        # 5. Рівень інтересу (технічно, ми його можемо залишити в кінці, щоб було зрозуміло)
        interest_line = f"Мій рівень зацікавлення: {interest_level} (0..9)."

        # 6. «Я не затягую розмову…»
        close_line = "Якщо я відмовляюся чи сумніваюся, роблю це стисло, без багатьох «До побачення»."

        # Збираємо все до купи
        # Додаємо chosen_objection, щоб відобразити «рівень інтересу» у вигляді
        # фрази/відмови/зацікавленості
        lines = [
            line_intro,
            child_text,
            profession_line,
            chosen_objection,
            interest_line,
            close_line,
            f"Наразі я {availability_info}."
        ]

        # Склеюємо
        prompt_text = " ".join(lines)

        prompts.append({
            "id": name,
            "text": prompt_text.strip()
        })

    # Зберігаємо
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=4)

    print(f"\n✅ Збережено {len(prompts)} промптів у {OUTPUT_FILE}!")

if __name__ == "__main__":
    generate_prompts()