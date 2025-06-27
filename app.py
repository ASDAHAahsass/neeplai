from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import logging

# Настройка
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)

# --- КОНФИГУРАЦИЯ API ---
API_BASE_URL = "http://5.35.114.38:8000/api/v1"
API_KEY = "ZOV"

# Список разрешенных моделей для безопасности
ALLOWED_MODELS = {
    "o3", "o4-mini", "o3-mini-high", "o3-mini",
    "gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-04-17",
    "gpt-4.5-preview", "gpt-4.1", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini"
}
# --------------------

try:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    logging.info(f"Клиент OpenAI для {API_BASE_URL} успешно инициализирован.")
except Exception as e:
    logging.error(f"Не удалось инициализировать клиент OpenAI: {e}")
    client = None

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# ===================================================================
# ===== ОБНОВЛЕННЫЙ МАРШРУТ БЕЗ ПОТОКОВОЙ ПЕРЕДАЧИ ==================
# ===================================================================
@app.route('/chat', methods=['POST'])
def handle_chat():
    if not client:
        return jsonify({"error": "Сервер API нейросети не инициализирован."}), 500

    data = request.json
    user_message = data.get('message')
    model_name = data.get('model')
    chat_history = data.get('history', [])

    if not user_message or not model_name:
        return jsonify({"error": "В запросе отсутствуют поля 'message' или 'model'."}), 400

    if model_name not in ALLOWED_MODELS:
        return jsonify({"error": f"Модель '{model_name}' не поддерживается."}), 400

    messages = chat_history
    messages.append({"role": "user", "content": user_message})

    try:
        # Убираем stream=True, чтобы получить ответ целиком
        response = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        ai_reply = response.choices[0].message.content
        return jsonify({'reply': ai_reply})

    except Exception as e:
        logging.error(f"Произошла ошибка при обращении к API: {e}")
        return jsonify({"error": f"Внутренняя ошибка сервера: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)