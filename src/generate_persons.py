import os
import json
import random
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
OUTPUT_FILE = os.path.join(DATA_DIR, "persons.json")
CITIES_FILE = os.path.join(DATA_DIR, "cities_output.json")

NUM_PERSONS = 10

# Распределения вероятностей для interest (0..9)
INTEREST_WEIGHTS = [
    0.10,  # 0
    0.08,  # 1
    0.08,  # 2
    0.08,  # 3
    0.10,  # 4
    0.12,  # 5
    0.14,  # 6
    0.12,  # 7
    0.10,  # 8
    0.08   # 9
]

# Распределения вероятностей для занятости (0..9)
AVAILABILITY_WEIGHTS = [
    0.08,  # 0
    0.08,  # 1
    0.10,  # 2
    0.12,  # 3
    0.12,  # 4
    0.12,  # 5
    0.10,  # 6
    0.10,  # 7
    0.10,  # 8
    0.08   # 9
]

CHILD_NAMES = [
    "Олег", "Оля", "Марічка", "Івась", "Сашко",
    "Соломія", "Катруся", "Петрик", "Андрійко", "Даринка"
]

def load_json(file_path: str):
    """Загружает JSON-данные из указанного файла (если он существует)."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено!")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if data else {}

def pick_level(weights):
    """Выбирает случайное значение от 0 до 9 по заданным вероятностям."""
    levels = list(range(10))
    return random.choices(levels, weights=weights, k=1)[0]

def generate_ukr_phone_number() -> str:
    """
    Генерируем украинский номер формата 0XXYYYYYYY (10 цифр).
    XX — код оператора, YYYYYYY — 7 цифр.
    """
    operators = ["50","63","66","67","68","91","92","93","94","95","96","97","98","99"]
    operator_code = random.choice(operators)
    # Генерируем 8 случайных цифр, из которых возьмём последние 7
    last_8_digits = random.randint(10_000_000, 99_999_999)
    last_7_str = str(last_8_digits)[1:]  # убираем первую цифру => 7 цифр
    return f"0{operator_code}{last_7_str}"

def load_cities():
    """
    Загружаем cities_output.json и возвращаем структуру [(city_key, prob, city_info), ...].
    city_info предполагает наличие полей "country" и "city" (список вариантов написания).
    """
    data = load_json(CITIES_FILE)
    result = []
    for city_key, city_info in data.items():
        prob = city_info.get("probability", 0.0)
        result.append((city_key, prob, city_info))
    return result

def pick_city(cities_data):
    """
    Из списка [(key, prob, info), ...] выбираем 1 город с учётом prob.
    Затем берём случайный вариант написания из info["city"] и чистим его
    от префикса вида "1) ", "2) ", и т.д.
    """
    if not cities_data:
        return ("Невідоме місто", "Невідома країна")

    keys = [cd[0] for cd in cities_data]
    probs = [cd[1] for cd in cities_data]
    infos = [cd[2] for cd in cities_data]

    chosen_idx = random.choices(range(len(keys)), weights=probs, k=1)[0]
    chosen_info = infos[chosen_idx]

    city_variants = chosen_info.get("city", [])
    if not city_variants:
        city_variants = [keys[chosen_idx]]

    chosen_variant = random.choice(city_variants)
    # Удаляем возможный префикс "1) ", "2) " и т.п.
    chosen_variant_clean = re.sub(r'^[0-9]+\)\s*', '', chosen_variant).strip()

    country = chosen_info.get("country", "Невідома країна")
    return (chosen_variant_clean, country)

def generate_person(cities_data):
    """
    Генерируем одну «персону»:
      - interest и mood/tone — числа (0..9),
      - выбираем город из cities_output.json,
      - не используем lifestyle.
    """
    names = [
        "Анна", "Іван", "Софія", "Максим", "Олексій", "Юлія",
        "Марія", "Олена", "Тетяна", "Олег", "Тарас", "Наталя",
        "Володимир", "Оксана", "Катерина", "Петро"
    ]
    hobbies = [
        "читання", "футбол", "подорожі", "малювання", "випікання",
        "шахи", "садівництво", "скандинавська ходьба", "велоспорт", "йога"
    ]
    professions = [
        "вчитель", "підприємець", "лікар", "дизайнер", "механік",
        "інженер", "журналіст", "перекладач", "фотограф", "менеджер"
    ]
    characters = ["емпат", "логік", "екстраверт", "інтроверт"]
    values = ["сім'я", "кар'єра", "екологія", "подорожі", "здоров'я"]
    marital_statuses = ["одружений", "розлучений", "самотній"]
    political_views_options = ["консерватор", "ліберал", "аполітичний", "поміркований"]

    name = random.choice(names)
    age = random.randint(20, 60)

    interest_level = pick_level(INTEREST_WEIGHTS)
    availability_level = pick_level(AVAILABILITY_WEIGHTS)
    phone = generate_ukr_phone_number()

    chosen_city, chosen_country = pick_city(cities_data)

    person = {
        "name": name,
        "age": age,
        "gender": random.choice(["чоловіча", "жіноча"]),
        "hobbies": random.choice(hobbies),
        "profession": random.choice(professions),
        "character": random.choice(characters),
        "values": random.choice(values),
        "marital_status": random.choice(marital_statuses),
        "political_views": random.choice(political_views_options),

        "interest": interest_level,  # число 0..9
        "tone": interest_level,      # число 0..9 (для примера)
        "mood": availability_level,  # число 0..9 (для примера)

        "phone": phone,
        "city": chosen_city,
        "country": chosen_country
    }

    # Дети, только если interest_level > 5
    if interest_level > 5:
        num_children = random.randint(1, 3)
        max_child_age = min(age - 15, 18)
        if max_child_age < 3:
            max_child_age = 3

        children = []
        for _ in range(num_children):
            c_age = random.randint(3, max_child_age)
            c_name = random.choice(CHILD_NAMES)
            children.append({"name": c_name, "age": c_age})

        person["children"] = children
    else:
        person["children"] = []

    return person

def generate_persons(file_path, count=NUM_PERSONS):
    # Загружаем данные о городах
    cities_data = load_cities()

    persons = [generate_person(cities_data) for _ in range(count)]
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(persons, file, ensure_ascii=False, indent=4)
    print(f"{count} персон успішно збережено у {file_path}!")

def main():
    # Загружаем города
    cities_data = load_cities()

    # Генерируем одну персону и выводим
    single_person = generate_person(cities_data)
    print("Приклад однієї персони (відображається у консолі):")
    print(json.dumps(single_person, ensure_ascii=False, indent=4))

    # Генерируем N персон и сохраняем в persons.json
    generate_persons(OUTPUT_FILE, NUM_PERSONS)

if __name__ == "__main__":
    main()