import json
import os
import csv

# Путь к директории с данными
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

def load_persons(file_path):
    """Загружает данные о личностях из JSON-файла."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_prompt(person):
    """Генерирует промпт для клиента на основе его характеристик."""
    if person['Наявність_дітей'] != "немає":
        children_info = f"Твої діти віку: {', '.join(map(str, person['Вік_дітей']))}."
    else:
        children_info = "У тебе немає дітей."

    return f"""
    Ти - {person["Ім'я"]}. Тобі {person['Вік']} років, ти {person['Стать']}.
    Ти працюєш {person['Професія']} і любиш проводити час, займаючись {person['Хобі']}.
    У тебе {person['Сімейний_стан']}, {person['Наявність_дітей']}. {children_info}
    Ти живеш {person['Тип життя']} життям і дотримуєшся {person['Політичні погляди']} поглядів.
    Ти {person['Характер']} за натурою і цінуєш {person['Цінності']}.
    Твій стиль спілкування - {person['Стиль розмови']}, і сьогодні ти {person['Настрій']}.
    Наразі ти {person['Тимчасовий стан']}. Коли ти чуєш пропозицію, пов'язану з математичними курсами для дітей, твоя перша реакція:
    "{person['Клієнтське заперечення']}".
    """

def save_prompts_to_csv(prompts, output_file):
    """Сохраняет сгенерированные промпты в файл CSV."""
    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Ідентифікатор", "Промпт"])
        for idx, prompt in enumerate(prompts, start=1):
            writer.writerow([f"prompt_{idx}", prompt.strip()])

def main():
    input_file = os.path.join(DATA_DIR, "persons.json")
    output_file = os.path.join(DATA_DIR, "prompts.csv")

    persons = load_persons(input_file)
    prompts = [generate_prompt(person) for person in persons]

    save_prompts_to_csv(prompts, output_file)
    print(f"Промпти успішно збережені у {output_file}!")

if __name__ == "__main__":
    main()