import os
import json
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
OUTPUT_FILE = os.path.join(DATA_DIR, "persons.json")

NUM_PERSONS = 10

# Распределения вероятностей (interest/availability)
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
    last_8_digits = random.randint(10_000_000, 99_999_999)  # от 10000000 до 99999999
    last_7_str = str(last_8_digits)[1:]  # убираем первую цифру => 7 цифр
    return f"0{operator_code}{last_7_str}"

def generate_person():
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
    lifestyle_options = ["міське", "сільське", "приміське"]
    political_views_options = ["консерватор", "ліберал", "аполітичний", "поміркований"]

    name = random.choice(names)
    age = random.randint(20, 60)

    # Выбираем interest и availability (числа 0..9)
    interest_level = pick_level(INTEREST_WEIGHTS)
    availability_level = pick_level(AVAILABILITY_WEIGHTS)

    phone = generate_ukr_phone_number()

    person = {
        "name": name,
        "age": age,
        "gender": random.choice(["чоловіча", "жіноча"]),
        "hobbies": random.choice(hobbies),
        "profession": random.choice(professions),
        "character": random.choice(characters),
        "values": random.choice(values),
        "marital_status": random.choice(marital_statuses),
        "lifestyle": random.choice(lifestyle_options),
        "political_views": random.choice(political_views_options),

        # Теперь только числа:
        "interest": interest_level,
        "tone": interest_level,  # Для наглядности: tone = interest
        "mood": availability_level,  # Или тоже interest, если хотите. Пример: mood = availability_level

        "phone": phone
    }

    # Дети только если interest_level > 5
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
    persons = [generate_person() for _ in range(count)]
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(persons, file, ensure_ascii=False, indent=4)
    print(f"{count} персон успішно збережено у {file_path}!")

if __name__ == "__main__":
    # Демонстрация одной персоны
    single = generate_person()
    print(json.dumps(single, ensure_ascii=False, indent=4))

    # Или сохранить несколько в файл:
    # generate_persons(OUTPUT_FILE, NUM_PERSONS)