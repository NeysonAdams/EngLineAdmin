import requests
from openai import OpenAI
import os
import json

api_key = "sk-proj-whd6Cycwl6et7vUnClQzT3BlbkFJwMblZsQZgRGQADM1LlGt"

client = OpenAI(
    # This is the default and can be omitted
    api_key=api_key,
)

def generate_Level(number, level, audience_language, lenguage):
    generation_prompt = f'''
    Ты — генератор учебных заданий по английскому языку уровня "{number}" для носителей языка: {audience_language}.
    Уровень сложности: {level}.

    📌 ВАЖНО:
    - Если уровень == "Beginner", ВСЕ ВОПРОСЫ должны быть на языке аудитории ({audience_language}). Ответы — на английском.
    - Если уровень == "Intermediate" или "Advanced", все вопросы и ответы — на английском.

    🎯 Твоя задача: сгенерировать **валидный JSON** строго по следующей структуре, подходящей для отправки в backend:

    Главный объект:
    {{
      "id": -1,
      "number": "{number}",
      "language": "{lenguage}",
      "exesizes": [ пакетов заданий должно быть минимум 3-4
        {{
          "id": -1,
          "name": "название пакета (на языке пользователя)",
          "type": "composite",
          "level": 1,
          "exesize": [
            ... (5 заданий из разных типов)
          ]
        }},
        ...
      ]
    }}

    Каждое задание внутри массива `exesize` может быть одного из следующих типов:

    ---

    1. **test_question**
    ```json
    {{
      "id": -1,
      "type": "test_question",
      "question": {{
        "id": -1,
        "question": "вопрос (на языке пользователя при уровне Beginner, иначе — на английском)",
        "test_answers": ["вариант 1", "вариант 2", "вариант 3", "вариант 4"],
        "right_var": 1
      }}
    }}

        input_question

    {{
      "id": -1,
      "type": "input_question",
      "inputquestion": {{
        "id": -1,
        "type": "add_missing" | "check_grammar" | "check_answer",
        "question": "вопрос (см. правила по уровню выше)",
        "answer": "ответ на английском",
        "isrecord": true
      }}
    }}

        audio_question

    {{
      "id": -1,
      "type": "audio_question",
      "audio": {{
        "id": -1,
        "question": "задание (см. правила по уровню выше)",
        "audio_query": "фраза для прослушивания на английском",
        "audio_url": "https://example.com/audio.mp3",
        "isrecord": false
      }}
    }}

        word_pair_exesize

    {{
      "id": -1,
      "type": "word_pair_exesize",
      "word_ex": {{
        "id": -1,
        "words": [
          {{
            "id": -1,
            "eng": "example",
            "rus": "пример",
            "uzb": "misol"
          }},
          ...
        ]
      }}
    }}

    🔒 ОБЯЗАТЕЛЬНО:

        Все поля id должны быть -1.

        Каждый пакет содержит 5 заданий случайных типов. сторого 5 заданий нельзя делать меньше

        Всего должно быть 4 пакета. нельзя что бы было меньше

        Вопросы должны соответствовать уровню сложности.

        Переводы в word_pair_exesize — ОБЯЗАТЕЛЬНО на русский и узбекский.

        Никакого текста вне JSON — Только чистый JSON-ответ.
        '''

    try:
        gpt_response = client.chat.completions.create(
            model="gpt-4-turbo",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": "ты професиональный контент креатор. ТЫ составляешь контент нужен для загрузки в приложение аналог duolingvo. "},
                {"role": "user", "content": generation_prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )

        content = gpt_response.choices[0].message.content
        result_json = json.loads(content)
        return result_json

    except Exception as e:
        print(f"Ошибка при генерации уровня: {e}")
        return None

main_route = "https://khamraeva.pythonanywhere.com"

def fetch_max_level(base_url, language):
    url = f"{base_url}/free/levels"
    params = {"language": language}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # выбросит исключение, если код != 200

        data = response.json()
        return data.get("max_level")

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def addLevel(level_data):
    url = f"{main_route}/free/add"
    response = requests.post(url, json=level_data)

    # Обработка ответа
    if response.ok:
        print("✅ Уровень успешно добавлен!")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.text)

def main():
    counter = 0
    while True:
        max_level = fetch_max_level(main_route, "uz")
        print("Current max level:", max_level)

        data = generate_Level(int(max_level) + 1, "Beginer", "Узбекский", "uz")
        print("Generated level:", int(max_level) + 1)

        addLevel(level_data=data)
        counter += 1

        if counter % 100 == 0:
            input("✅ Сгенерировано 100 уровней. Нажмите Enter, чтобы продолжить (или Ctrl+C для выхода)...")

if __name__ == '__main__':
    main()