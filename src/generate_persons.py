import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
OUTPUT_FILE = os.path.join(DATA_DIR, "persons.json")

# Кількість персон
NUM_PERSONS = 10

def generate_person():
    """Генерує випадкову особистість із розширеним списком і визначає рівень інтересу (0..9)."""
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
    moods = ["гарний", "поганий", "нейтральний"]
    conversation_styles = ["м'який", "грубий", "прямолінійний", "саркастичний", "доброзичливий"]
    availability_states = ["зайнятий", "немає часу", "доступний зараз", "працюю"]
    political_views_options = ["консерватор", "ліберал", "аполітичний", "поміркований"]

    name = random.choice(names)
    age = random.randint(20, 60)

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
        "conversation_style": random.choice(conversation_styles),
        "availability": random.choice(availability_states),
        "mood": random.choice(moods),
        # поле objection видалено
        "interest_level": 0  # Поставимо тимчасово 0, потім визначимо нижче
    }

    # Генеруємо дітей
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

    # Логіка визначення interest_level
    # 0: немає дітей -> interest_level = 0
    # якщо діти <5 років або >12 років -> interest_level у [1..4]
    # якщо є принаймні одна дитина 5..12 -> [2..9]
    
    has_children_any = (person["has_children"] != "немає")
    if not has_children_any:
        # немає дітей => 0
        person["interest_level"] = 0
    else:
        # подивимось, які діти
        child_ages = person["children_ages"]
        # Перевіряємо, чи є хоч одна дитина 5..12
        any_in_5_12 = any(5 <= age_c <= 12 for age_c in child_ages)
        if any_in_5_12:
            # interest_level у діапазоні [2..9]
            person["interest_level"] = random.randint(2, 9)
        else:
            # якщо всі діти <5 або >12 => [1..4]
            person["interest_level"] = random.randint(1, 4)

    return person

def generate_persons(file_path, count=NUM_PERSONS):
    persons = [generate_person() for _ in range(count)]
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(persons, file, ensure_ascii=False, indent=4)
    print(f"{count} персон успішно збережено у {file_path}!")

if __name__ == "__main__":
    generate_persons(OUTPUT_FILE, count=NUM_PERSONS)