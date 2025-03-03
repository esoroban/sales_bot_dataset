import json
import openai
import os
from dotenv import load_dotenv
import uuid

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Загрузка исходного файла
with open('data/ua.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Ограничение первыми 5 городами для проверки
limited_data = data[:5]

# Подсчёт суммарного населения для вычисления вероятностей
population_total = sum(int(city["population"]) for city in limited_data)

result = {}

# Функция генерации вариантов названий через ИИ
def generate_city_variants(city_name):
    prompt = f"""Приведи четыре варианта названия города {city_name}:
1) На русском языке
2) На украинском языке
3) На суржике
4) С грамматической ошибкой

Ответ дай в формате JSON списком (например: [\"русский\", \"украинский\", \"суржик\", \"ошибка\"]). Только сам список, без объяснений."""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    city_variants = json.loads(response.choices[0].message.content)
    return city_variants

# Перебор первых 5 городов и генерация названий
for idx, city in enumerate(limited_data, 1):
    variants = generate_city_variants(city['city'])

    result[city['city']] = {
        "id": idx,
        "country": "Ukraine",
        "city": variants,
        "population": city["population"],
        "probability": round(int(city["population"]) / population_total, 6)
    }

# Сохраняем в новый файл
with open('data/cities_transformed.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ Файл создан: data/cities_transformed.json")
