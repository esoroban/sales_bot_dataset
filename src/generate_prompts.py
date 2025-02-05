import os
import json
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
PERSONS_FILE = os.path.join(DATA_DIR, "persons.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "prompts.json")

NUM_PROMPTS = 10

# Рівні інтересу
INTEREST_LEVELS_POSITIVE = ["низький інтерес", "помірний інтерес", "високий інтерес"]
INTEREST_LEVELS_NEGATIVE = ["немає інтересу", "мінімальний інтерес"]

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

def generate_prompts():
    """
    Генерує “первинні” промпти клієнта з урахуванням:
      1. Логіки віку дітей (5–12 років): якщо діти поза цим віком, зазвичай нижчий інтерес.
      2. З певною ймовірністю клієнт може мати «помірний інтерес» навіть без дітей 5..12.
      3. Залежно від об’єкції (objection) і interest_level, текст може бути від повної відмови до легкого зацікавлення.
      4. Формат 3–4 речення, без зайвих ввічливостей.
      5. «Помірний інтерес» має відобразитись у відсутності категоричної відмови, 
         а в тоні «Можливо, але не зараз» або «Я ще думаю…».
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

        valid_ages = [child_age for child_age in children_ages if 5 <= child_age <= 12]

        raw_objection = person.get("objection", "").strip()
        if has_children and not raw_objection:
            raw_objection = "Мої діти й без того зайняті"
        elif not has_children and not raw_objection:
            raw_objection = "Це мені неактуально"

        # Якщо "дитини немає часу" без дітей
        if not has_children and "дитини" in raw_objection.lower():
            raw_objection = "Це мені неактуально"

        # Визначаємо інтерес
        if valid_ages:
            interest_level = random.choice(INTEREST_LEVELS_POSITIVE)  
        else:
            # Якщо діти поза віком 5..12, з ймовірністю 0.3 обираємо "помірний інтерес"
            # інакше беремо негатив
            if random.random() < 0.3:
                interest_level = "помірний інтерес"
            else:
                interest_level = random.choice(INTEREST_LEVELS_NEGATIVE)

        # Побудова причини відмови/обмеження
        if has_children:
            if not valid_ages:
                age_objection = "Мої діти не підходять за віком 5–12 років"
            else:
                age_objection = raw_objection
        else:
            age_objection = raw_objection

        # Текст:
        if has_children:
            ages_str = ", ".join(map(str, children_ages))
            refusal_reason = f"У мене {len(children_ages)} діт{'и' if len(children_ages) > 1 else 'ина'} ({ages_str} років)."
            if not valid_ages:
                refusal_reason += " Вони поза межами 5–12, тому курс поки не здається нам доречним."
            else:
                refusal_reason += f" Хоча їхній вік збігається з вимогами, однак {age_objection.lower()}."
        else:
            refusal_reason = "У мене немає дітей, тому ці курси мені не надто потрібні."

        # Якщо interest_level == "помірний інтерес", 
        # трохи підкоригуємо формулювання, щоб не було "різкої відмови".
        if interest_level == "помірний інтерес":
            # Якщо raw_objection звучить дуже категорично, 
            # перепишемо його в більш м'яку форму:
            if raw_objection in ["Мені це не цікаво.", "Це мені неактуально", "Дорого."]:
                soft_reason = "Я поки що не впевнена, чи це нам підійде."
                if not has_children:
                    refusal_reason = "У мене немає дітей, та все ж допускаю, що методика «Соробан» може бути корисною в майбутньому."
                else:
                    refusal_reason = "Попри мої сумніви, можливо, це стане нам у пригоді, якщо знайдеться час."
                age_objection = soft_reason

        # Професія + характер
        if character.lower() == "емпат":
            profession_line = (
                f"Я {profession}, люблю {hobbies}, і як емпат враховую почуття інших, "
                f"але {age_objection.lower()}."
            )
        else:
            profession_line = (
                f"Я {profession}, люблю {hobbies}, і як {character} "
                f"дивлюся на все раціонально, тож {age_objection.lower()}."
            )

        story_lines = []
        # Вступ
        if age:
            story_lines.append(f"Мене звати {name}, мені {age} років, веду {lifestyle} спосіб життя.")
        else:
            story_lines.append(f"Мене звати {name}, я живу в {lifestyle} місцевості.")
        # професія + причина
        story_lines.append(profession_line)
        # відмова/причина
        story_lines.append(refusal_reason)
        # рівень інтересу
        story_lines.append(f"Мій рівень зацікавлення: {interest_level}.")

        # Уникаємо довгих прощань
        story_lines.append("Якщо відмовляюся, роблю це стисло і без нескінченних «До побачення».")

        prompt_text = " ".join(story_lines)

        availability_info = person.get("availability", "невідомо")
        prompt_text += f" Наразі я {availability_info}."

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