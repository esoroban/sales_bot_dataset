import os
import json
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
OUTPUT_FILE = os.path.join(DATA_DIR, "persons.json")
CITIES_FILE = os.path.join(DATA_DIR, "cities_transformed.json")

NUM_PERSONS = 10

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

with open(CITIES_FILE, 'r', encoding='utf-8') as f:
    cities_data = json.load(f)

city_names = []
city_probs = []
for city_info in cities_data.values():
    city_names.append(city_info["city"])
    city_probs.append(city_info["probability"])

def generate_person():
    names = ["Анна", "Іван", "Софія", "Максим", "Олексій", "Юлія",
             "Марія", "Олена", "Тетяна", "Олег", "Тарас", "Наталя",
             "Володимир", "Оксана", "Катерина", "Петро"]
    hobbies = ["читання", "футбол", "подорожі", "малювання", "випікання",
               "шахи", "садівництво", "скандинавська ходьба", "велоспорт", "йога"]
    professions = ["вчитель", "підприємець", "лікар", "дизайнер", "механік",
                   "інженер", "журналіст", "перекладач", "фотограф", "менеджер"]
    characters = ["емпат", "логік", "екстраверт", "інтроверт"]
    values = ["сім'я", "кар'єра", "екологія", "подорожі", "здоров'я"]
    marital_statuses = ["одружений", "розлучений", "самотній"]
    children_statuses = ["немає", "одна дитина", "дві дитини", "багатодітна сім'я"]
    political_views_options = ["консерватор", "ліберал", "аполітичний", "поміркований"]

    children_status = random.choice(children_statuses)
    # "Желание записаться на курс" должно быть положительным (>4) только при наличии детей.
    if children_status != "немає":
        desire_level = random.randint(5, 9)
    else:
        desire_level = random.randint(0, 4)

    tone_level = random.randint(0, 9)
    mood_level = random.randint(0, 9)
    availability_level = random.randint(0, 9)

    chosen_city = random.choices(city_names, weights=city_probs, k=1)[0]

    person = {
        "name": random.choice(names),
        "age": random.randint(20, 60),
        "gender": random.choice(["чоловіча", "жіноча"]),
        "hobbies": random.choice(hobbies),
        "profession": random.choice(professions),
        "character": random.choice(characters),
        "values": random.choice(values),
        "marital_status": random.choice(marital_statuses),
        "has_children": children_status,
        "political_views": random.choice(political_views_options),
        "желание записаться на курс": INTEREST_DESCRIPTIONS[desire_level],
        "tone": TONE_DESCRIPTIONS[tone_level],
        "mood": MOOD_DESCRIPTIONS[mood_level],
        "availability": AVAILABILITY_DESCRIPTIONS[availability_level],
        "city": chosen_city,
        "country": "Ukraine"
    }

    return person

def generate_persons(file_path, count=NUM_PERSONS):
    persons = [generate_person() for _ in range(count)]
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(persons, file, ensure_ascii=False, indent=4)
    print(f"{count} персон успішно збережено у {file_path}!")

if __name__ == "__main__":
    generate_persons(OUTPUT_FILE, count=NUM_PERSONS)