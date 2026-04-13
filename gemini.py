import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-flash-latest"


def generate_summary(text: str) -> str:
    if not GEMINI_API_KEY:
        return "Ошибка: GEMINI_API_KEY не задан"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Ты помощник для анализа встреч.\n"
                            "Сделай структурированное резюме:\n"
                            "- краткое summary\n"
                            "- ключевые решения\n"
                            "- задачи (action items)\n"
                            "- важные моменты\n\n"
                            f"Текст:\n{text}"
                        )
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        data = response.json()

        # если API вернул ошибку
        if "error" in data:
            return f"Ошибка Gemini API: {data['error'].get('message', data['error'])}"

        # защита от нестандартного ответа
        if "candidates" not in data:
            return f"Неожиданный ответ API:\n{data}"

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except requests.exceptions.RequestException as e:
        return f"Сетевая ошибка Gemini API: {str(e)}"

    except Exception as e:
        return f"Ошибка обработки ответа: {str(e)}"