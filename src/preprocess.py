import json
import re
import os

# Пути к файлам
DATA_PATH = "data/dialogues.json"  # Исходный файл
OUTPUT_PATH = "data/training_dataset.jsonl"  # Финальный датасет

def fix_dataset_format(data):
    """
    Исправляет формат диалогов:
    - Убирает stop_dialogue(...)
    - Добавляет стартовый контекст
    - Удаляет дублирующиеся сообщения
    - Сохраняет хотя бы одно сообщение на каждую пару
    """
    fixed_data = []
    total_entries = 0  
    removed_entries = 0  

    for conv in data:
        conversation = conv["dialogue"]
        context = ""
        last_role = None  

        for i, message in enumerate(conversation):
            role = message["role"]
            text = message["message"]

            # Убираем stop_dialogue(...)
            text = re.sub(r'stop_dialogue\(".*?"\)', "", text).strip()

            # Убираем повторное приветствие от sales_bot
            if i == 1 and role == "sales_bot":
                continue

            entry = {
                "question": text if role == "client" else "",
                "context": context,
                "response": text if role == "sales_bot" else ""
            }

            # Добавляем стартовый контекст только 1 раз
            if i == 0:
                context = "<|user|> Клієнт підключився до розмови.\n\n<|assistant|> Вітаю! Я – ШІ школи усного рахунку «Соробан». Чи є у вас хвилинка поспілкуватися?"

            # Обновляем контекст
            context += f"\n\n<|{role}|> {text}"

            # Проверяем, что хотя бы что-то есть (не удаляем всё)
            if entry["question"] or entry["response"]:
                fixed_data.append(entry)
                total_entries += 1
            else:
                removed_entries += 1
                print(f"⚠️ Пропущено сообщение: {entry}")

    print(f"📊 Исходных записей: {len(data)}, итоговых записей: {total_entries}, удалено: {removed_entries}")
    return fixed_data


def preprocess_data():
    """Основной процессинг данных"""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Файл {DATA_PATH} не найден!")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"📂 Загружено {len(raw_data)} диалогов из {DATA_PATH}")

    # Фиксим и форматируем датасет
    fixed_dataset = fix_dataset_format(raw_data)

    # Сохраняем в JSONL
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f_out:
        for entry in fixed_dataset:
            f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ Датасет успешно обработан и сохранен в {OUTPUT_PATH}")


if __name__ == "__main__":
    preprocess_data()