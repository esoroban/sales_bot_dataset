import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

def generate_person():
    """Генерирует случайную личность."""
    names = ["Анна", "Іван", "Софія", "Максим", "Олексій", "Юлія"]
    hobbies = ["читання", "футбол", "подорожі", "малювання", "випікання"]
    professions = ["вчитель", "підприємець", "лікар", "дизайнер", "механік"]
    characters = ["емпат", "логік", "екстраверт", "інтроверт"]
    values = ["сім'я", "кар'єра", "екологія", "подорожі"]
    statuses = ["одружений", "розлучений", "самотній"]
    children_status = ["немає", "одна дитина", "дві дитини", "багатодітна сім'я"]
    moods = ["гарний", "поганий", "нейтральний"]
    conversation_styles = ["м'який", "грубий", "прямолінійний", "саркастичний"]
    temporary_states = ["зайнятий", "немає часу", "доступний зараз"]

    # Генерация базовых данных
    name = random.choice(names)
    age = random.randint(20, 60)
    person = {
        "Ім'я": name,
        "Вік": age,
        "Стать": random.choice(["чоловіча", "жіноча"]),
        "Хобі": random.choice(hobbies),
        "Професія": random.choice(professions),
        "Характер": random.choice(characters),
        "Цінності": random.choice(values),
        "Сімейний_стан": random.choice(statuses),
        "Наявність_дітей": random.choice(children_status),
        "Тип життя": random.choice(["міське", "сільське", "приміське"]),
        "Політичні погляди": random.choice(["консерватор", "ліберал", "аполітичний"]),
        "Стиль розмови": random.choice(conversation_styles),
        "Тимчасовий стан": random.choice(temporary_states),
        "Настрій": random.choice(moods),
        "Клієнтське заперечення": random.choice([
            "Мені це не цікаво.", "Дорого.", "У дитини немає часу на додаткові заняття.",
            "Ми поки не плануємо додаткові заняття для дитини."
        ]),
    }

    # Генерация возраста детей
    if person["Наявність_дітей"] != "немає":
        if person["Наявність_дітей"] == "одна дитина":
            num_children = 1
        elif person["Наявність_дітей"] == "дві дитини":
            num_children = 2
        else:
            num_children = random.randint(3, 5)

        # Генерируем возраст детей с условием разницы в возрасте минимум 15 лет
        person["Вік_дітей"] = [
            random.randint(3, min(person["Вік"] - 15, 18)) for _ in range(num_children)
        ]
    else:
        person["Вік_дітей"] = []

    return person

def generate_persons(file_path, count=10):
    """Генерирует JSON-файл с несколькими личностями."""
    persons = [generate_person() for _ in range(count)]
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(persons, file, ensure_ascii=False, indent=4)
    print(f"{count} персон успішно збережено у {file_path}!")

if __name__ == "__main__":
    output_file = os.path.join(DATA_DIR, "persons.json")
    generate_persons(output_file, count=10)