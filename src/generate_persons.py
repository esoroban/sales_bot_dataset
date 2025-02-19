import os
import json
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
OUTPUT_FILE = os.path.join(DATA_DIR, "persons.json")

# Кількість персон для генерації
NUM_PERSONS = 10

# Фіксований розподіл імовірностей для рівня інтересу (0..9)
INTEREST_WEIGHTS = [
    0.30,  # 0 = не цікаво зовсім, грубий тон, поганий настрій
    0.15,  # 1
    0.12,  # 2
    0.10,  # 3
    0.08,  # 4
    0.07,  # 5
    0.06,  # 6
    0.05,  # 7
    0.04,  # 8
    0.03   # 9 = дуже цікаво, м'який тон, гарний настрій
]

# Розподіл для рівня зайнятості (0..9) - незалежний параметр
AVAILABILITY_WEIGHTS = [
    0.25,  # 0 = категорично зайнятий
    0.15,  # 1
    0.13,  # 2
    0.12,  # 3
    0.10,  # 4
    0.08,  # 5
    0.07,  # 6
    0.06,  # 7
    0.04,  # 8
    0.03   # 9 = вільний, можу говорити
]

# Словесне представлення рівнів
INTEREST_DESCRIPTIONS = [
    "Не цікаво зовсім", "Майже не цікаво", "Слабкий інтерес", "Низький інтерес", 
    "Помірний інтерес", "Дещо цікаво", "Зацікавлений", "Досить цікавить", 
    "Дуже цікаво", "Максимально зацікавлений"
]

TONE_DESCRIPTIONS = [
    "Грубий і неприємний", "Різкий", "Холодний", "Нейтральний", 
    "Стримано-доброзичливий", "Помірно теплий", "Привітний", "Дружній", 
    "М'який і уважний", "Максимально ввічливий та доброзичливий"
]

MOOD_DESCRIPTIONS = [
    "Дуже поганий настрій", "Роздратований", "Незадоволений", "Скептичний",
    "Нейтральний", "Помірно позитивний", "Гарний настрій", "Оптимістичний",
    "Радісний", "Енергійний і дуже доброзичливий"
]

AVAILABILITY_DESCRIPTIONS = [
    "Категорично зайнятий", "Дуже зайнятий", "Мало часу", "Помірно зайнятий",
    "Може виділити трохи часу", "Відносно вільний", "Може говорити, але ненадовго",
    "Досить вільний", "Майже вільний", "Повністю доступний"
]

def pick_level(weights):
    """Повертає випадкове значення від 0 до 9 за заданими ймовірностями."""
    levels = list(range(10))  # 0..9
    return random.choices(levels, weights=weights, k=1)[0]

def generate_person():
    """Генерує випадкову особистість із рівнем інтересу, зайнятості та тону розмови."""
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
    children_statuses = ["немає", "одна дитина", "дві дитини", "багатодітна сім'я"]
    political_views_options = ["консерватор", "ліберал", "аполітичний", "поміркований"]

    name = random.choice(names)
    age = random.randint(20, 60)

    # Генеруємо рівень інтересу, тону, настрою
    interest_level = pick_level(INTEREST_WEIGHTS)
    availability_level = pick_level(AVAILABILITY_WEIGHTS)

    person = {
        "name": name,
        "age": age,
        "gender": random.choice(["чоловіча", "жіноча"]),
        "hobbies": random.choice(hobbies),
        "profession": random.choice(professions),
        "character": random.choice(characters),
        "values": random.choice(values),
        "marital_status": random.choice(marital_statuses),
        "has_children": random.choice(children_statuses),
        "lifestyle": random.choice(["міське", "сільське", "приміське"]),
        "political_views": random.choice(political_views_options),

        # Лише словесні рівні
        "interest": INTEREST_DESCRIPTIONS[interest_level],
        "tone": TONE_DESCRIPTIONS[interest_level],
        "mood": MOOD_DESCRIPTIONS[interest_level],
        "availability": AVAILABILITY_DESCRIPTIONS[availability_level]
    }

    # Генеруємо дітей (якщо є)
    if person["has_children"] != "немає":
        if person["has_children"] == "одна дитина":
            num_children = 1
        elif person["has_children"] == "дві дитини":
            num_children = 2
        else:
            num_children = random.randint(3, 5)

        max_child_age = min(age - 15, 18)
        if max_child_age < 3:
            max_child_age = 3

        person["children_ages"] = [
            random.randint(3, max_child_age) for _ in range(num_children)
        ]
    else:
        person["children_ages"] = []

    return person

def generate_persons(file_path, count=NUM_PERSONS):
    persons = [generate_person() for _ in range(count)]
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(persons, file, ensure_ascii=False, indent=4)
    print(f"{count} персон успішно збережено у {file_path}!")

if __name__ == "__main__":
    generate_persons(OUTPUT_FILE, count=NUM_PERSONS)