import os
import json

# Шлях до файлів
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PERSONS_FILE = os.path.join(DATA_DIR, "persons.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "prompts.json")

# Кількість клієнтів
NUM_PROMPTS = 2

# Доступні рівні інтересу
INTEREST_LEVELS = ["слабкий інтерес", "зацікавлений, але сумнівається"]

def load_persons(file_path):
    """Завантажує список готових особистостей з JSON."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено! Спочатку запустіть generate_persons.py")
        return []
    
    with open(file_path, "r", encoding="utf-8") as file:
        persons = json.load(file)
    
    if not persons:
        print("❌ Помилка: Файл персон порожній!")
    
    return persons

def generate_prompts():
    """Генерує промпти на основі вже готових особистостей."""
    persons = load_persons(PERSONS_FILE)
    if not persons:
        print("❌ Неможливо створити промпти без персон!")
        return

    prompts = []

    for person in persons[:NUM_PROMPTS]:
        # Чи є у клієнта діти
        has_children = bool(person.get("children_ages", []))

        # Визначаємо рівень інтересу
        interest_level = "немає інтересу" if not has_children else INTEREST_LEVELS[0]  # за замовчуванням "слабкий інтерес"

        # Формуємо опис дітей
        children_text = f"Маю дітей: {', '.join(map(str, person['children_ages']))}" if has_children else "Немає дітей."

        # Формуємо промпт
        prompt_text = (
            f"Ти {person['name']}, {person['profession']}. "
            f"Живеш {person['lifestyle']}. "
            f"Твоє хобі — {person['hobbies']}. "
            f"Твій характер — {person['character']}. "
            f"{children_text}. "
            f"Рівень інтересу: {interest_level}. "
            f"Типова відмова: {person.get('objection', 'Без заперечень')}. "
            f"Доступність для розмови: {person.get('availability', 'Невідомо')}. "
            f"Ти не повторюєш повідомлення співрозмовника. "
            f"Ти відповідаєш стисло, але уникаєш повторів."
        )

        prompts.append({"id": person["name"], "text": prompt_text})

    # Запис у JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=4)

    print(f"✅ Збережено {NUM_PROMPTS} промптів у {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_prompts()