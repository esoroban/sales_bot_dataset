import os
import json
from dotenv import load_dotenv
import openai

# Загружаем API-ключ
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Пути к файлам
input_file = "data/ua.json"
output_file = "data/cities_output.json"

# Читаем входной JSON
with open(input_file, "r", encoding="utf-8") as f:
    cities_data = json.load(f)

# Функция для безопасного получения численности населения
def safe_int(value):
    try:
        return int(value.replace(" ", "")) if value.strip() else 0
    except ValueError:
        return 0

# Считаем общее население (фильтруем города без данных о населении)
total_population = sum(safe_int(city.get("population", "0")) for city in cities_data)

# Функция для генерации вариантов названий города
def generate_city_variants(city_name):
    prompt = f"Генерируй четыре варианта названия города {city_name}: 1) русский, 2) украинский, 3) на суржике, 4) с ошибкой."
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=50
    )
    return response["choices"][0]["message"]["content"].strip().split("\n")

# Ограничиваем обработку 50 городами
cities_data = cities_data[:1000]

# Обрабатываем данные по городам
cities_output = {}

for city in cities_data:
    city_name = city["city"]
    population = safe_int(city.get("population", "0"))
    probability = round(population / total_population, 6) if total_population > 0 else 0

    try:
        city_variants = generate_city_variants(city_name)
        if len(city_variants) < 4:
            raise ValueError("Недостаточно вариантов названий города")
    except Exception as e:
        print(f"Ошибка генерации для {city_name}: {e}")
        city_variants = [city_name] * 4  # Если ошибка, дублируем оригинальное имя

    cities_output[city_name] = {
        "country": "Ukraine",
        "city": city_variants,
        "probability": probability
    }

# Сохраняем результат
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cities_output, f, ensure_ascii=False, indent=4)

# Выводим 3 примера
sample_keys = list(cities_output.keys())[:3]
for key in sample_keys:
    print(f"{key}: {cities_output[key]}")