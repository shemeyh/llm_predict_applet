from flask import Flask, request, jsonify, render_template
from logic.forecast_single_question import forecast_single_question
import os
import asyncio
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forecast', methods=['POST'])
def forecast():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    question = data.get('question')
    resolution_criteria = data.get('resolution_criteria')
    news = data.get('news')  # Optional
    openai_api_key = data.get('openai_api_key')

    missing_fields = []
    if not question:
        missing_fields.append("question")
    if not resolution_criteria:
        missing_fields.append("resolution_criteria")
    if not openai_api_key:
        missing_fields.append("openai_api_key")

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    original_api_key = os.environ.get('OPENAI_API_KEY')
    os.environ['OPENAI_API_KEY'] = openai_api_key

    try:
        question_details = {
            "title": question,
            "description": question,  # Using question as description for now
            "resolution_criteria": resolution_criteria,
            "fine_print": "",  # Default value
            "forecast_date": datetime.now().strftime("%Y-%m-%d")  # Current date
        }

        # Call the forecasting pipeline
        # Using default values for cache_seed, is_woc, num_of_experts
        result = asyncio.run(forecast_single_question(
            question_details=question_details,
            news_text=news,
            cache_seed=42,
            is_woc=False,
            num_of_experts=None 
        ))
        return jsonify(result)

    except Exception as e:
        print(f"Error during forecasting: {e}")
        return jsonify({"error": "An error occurred during forecasting", "details": str(e)}), 500
    finally:
        # Restore the original API key
        if original_api_key is None:
            del os.environ['OPENAI_API_KEY']
        else:
            os.environ['OPENAI_API_KEY'] = original_api_key

if __name__ == '__main__':
    app.run(debug=True)
