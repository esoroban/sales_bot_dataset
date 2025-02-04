import os
import json
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PERSONS_FILE = os.path.join(DATA_DIR, "persons.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "prompts.json")

NUM_PROMPTS = 2

INTEREST_LEVELS_POSITIVE = ["низький інтерес", "помірний інтерес", "високий інтерес"]
INTEREST_LEVELS_NEGATIVE = ["немає інтересу", "мінімальний інтерес"]

def load_persons(file_path):
    """Завантажує список готових особистостей з JSON."""
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено! Спочатку запустіть generate_persons.py.")
        return []
    
    with open(file_path, "r", encoding="utf-8") as file:
        persons = json.load(file)
    
    if not persons:
        print("❌ Помилка: Файл персон порожній!")
    
    return persons

def generate_prompts():
    """
    Генерує “первинні” промпти клієнта з урахуванням:
     1. Логіки віку дітей (5–12 років) — якщо діти не підходять, клієнт переважно не зацікавлений.
     2. Випадкової генерації рівня інтересу (низький, помірний, високий чи немає інтересу).
     3. Врахування професії, характеру, хобі, причини відмови.
     4. Формату 3–4 речення, без зайвих ввічливостей і дублювання пропозицій.
     5. Додано жорстку вимогу: якщо клієнт відмовляється, він не продовжує діалог 
        безкінечними “До побачення” чи “Якщо що, звертайтесь”.
    """

    persons = load_persons(PERSONS_FILE)
    if not persons:
        print("❌ Неможливо створити промпти без персон!")
        return

    prompts = []

    for person in persons[:NUM_PROMPTS]:
        name = person.get("name", "Невідомий")
        age = person.get("age", "")
        profession = person.get("profession", "безробітний")
        lifestyle = person.get("lifestyle", "міське")
        hobbies = person.get("hobbies", "не вказані")
        character = person.get("character", "невизначений")
        children_ages = person.get("children_ages", [])
        has_children = bool(children_ages)

        # Які діти у віці 5..12
        valid_ages = [child_age for child_age in children_ages if 5 <= child_age <= 12]

        raw_objection = person.get("objection", "").strip()
        if has_children and not raw_objection:
            raw_objection = "Мої діти й без того зайняті"
        elif not has_children and not raw_objection:
            raw_objection = "Це мені неактуально"

        # Якщо згадується “дитини немає часу”, а дітей немає
        if not has_children and "дитини" in raw_objection.lower():
            raw_objection = "Це мені неактуально"

        # Визначимо рівень інтересу
        if valid_ages:
            interest_level = random.choice(INTEREST_LEVELS_POSITIVE)
        else:
            interest_level = random.choice(INTEREST_LEVELS_NEGATIVE)

        # Логіка відмови/причини
        if has_children:
            if not valid_ages:
                age_objection = "Мої діти не підходять за віком 5–12 років"
            else:
                age_objection = raw_objection
        else:
            age_objection = raw_objection

        if has_children:
            ages_str = ", ".join(map(str, children_ages))
            refusal_reason = f"У мене {len(children_ages)} діт{'и' if len(children_ages) > 1 else 'ина'} ({ages_str} років)."
            if not valid_ages:
                refusal_reason += " Вони поза межами 5–12, тому нам це не підходить."
            else:
                refusal_reason += f" Хоч вік збігається з вимогами, однак {age_objection.lower()}."
        else:
            refusal_reason = "У мене немає дітей, тому ці курси мені не потрібні."

        if character.lower() == "емпат":
            profession_line = (
                f"Я {profession}, люблю {hobbies}, і як емпат враховую почуття інших, "
                f"але {age_objection.lower()}."
            )
        else:
            profession_line = (
                f"Я {profession}, люблю {hobbies}, і як {character} "
                f"оцінюю все прагматично, тож {age_objection.lower()}."
            )

        story_lines = []

        # Вступ
        if age:
            story_lines.append(f"Мене звати {name}, мені {age} років, веду {lifestyle} спосіб життя.")
        else:
            story_lines.append(f"Мене звати {name}, я живу в {lifestyle} місцевості.")

        story_lines.append(profession_line)
        story_lines.append(refusal_reason)
        story_lines.append(f"Мій рівень зацікавлення: {interest_level}.")

        # Вимога не дублювати пропозиції, не затягувати діалог
        story_lines.append(
            "Якщо я вже відмовився, не затягую розмову і не повторюю «До побачення» багато разів."
        )

        prompt_text = " ".join(story_lines)

        availability_info = person.get("availability", "невідомо")
        prompt_text += f" Наразі я {availability_info}."

        prompts.append({
            "id": name,
            "text": prompt_text.strip()
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=4)

    print(f"✅ Збережено {len(prompts)} промптів у {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_prompts()