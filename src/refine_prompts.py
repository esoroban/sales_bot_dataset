import os
import openai
import csv

# Укажите путь к .env-файлу, где хранится OPENAI_API_KEY
from dotenv import load_dotenv
load_dotenv()

# Инициализация OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Пути к файлам
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
INPUT_FILE = os.path.join(DATA_DIR, "prompts.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "refined_prompts.csv")

def refine_prompt(prompt):
    """Использует OpenAI API для исправления логических ошибок в промпте."""
    system_prompt = """
    Ты умный редактор текста. Твоя задача:
    - Проверить текст на логические ошибки (например, возраст родителей и детей, несовместимость профессии и возраста, семейного положения и т. д.).
    - Исправить текст, сохраняя его структуру и общий смысл.
    - Убедиться, что текст логически последовательный.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Ошибка при обработке промпта: {e}")
        return prompt  # Если произошла ошибка, возвращаем исходный промпт

def refine_prompts(input_file, output_file):
    """Читает промпты, исправляет их и сохраняет в новый CSV."""
    with open(input_file, mode='r', encoding='utf-8') as infile, \
         open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Читаем заголовок и пишем его в новый файл
        header = next(reader)
        writer.writerow(header)
        
        # Обрабатываем каждый промпт
        for row in reader:
            prompt_id, prompt = row
            refined_prompt = refine_prompt(prompt)
            writer.writerow([prompt_id, refined_prompt])
            print(f"Промпт {prompt_id} обработан.")

if __name__ == "__main__":
    refine_prompts(INPUT_FILE, OUTPUT_FILE)
    print(f"Откорректированные промпты сохранены в {OUTPUT_FILE}.")