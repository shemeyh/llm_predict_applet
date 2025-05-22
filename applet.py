import asyncio
import dotenv
import os
from datetime import datetime
# Assuming logic.forecase_single_question will be created later
from logic.forecast_single_question import forecast_single_question

def get_user_question():
  """Prompts the user for the question and returns it as a string."""
  print("\n--- Enter Your Question ---")
  print("Please type the question you want a forecast for (e.g., 'Will X happen by Y date?'):")
  question = input("> ")
  return question

def get_resolution_criteria():
  """Prompts the user for the resolution criteria and returns it as a string."""
  print("\n--- Enter Resolution Criteria ---")
  print("Please specify how this question will be judged true or false (e.g., 'Based on official report from Z'):")
  resolution_criteria = input("> ")
  return resolution_criteria

def get_user_news():
  """Prompts the user to input news articles and returns them as a string."""
  print("\n--- Provide Relevant News Articles ---")
  print("Paste any relevant news article text below. Press Ctrl+D (or Ctrl+Z on Windows) then Enter when you're done:")
  lines = []
  while True:
    try:
      line = input()
      lines.append(line)
    except EOFError:
      break
  return "\n".join(lines)

async def run_forecast(user_question: str, user_resolution_criteria: str, user_news: str):
  """Runs the forecasting logic with the user's input."""
  final_result = None
  summarization = None
  question_details = {
      "title": user_question,
      "description": f"{user_question}\n\nResolution Criteria:\n{user_resolution_criteria}",
      "fine_print": "",
      "resolution_criteria": user_resolution_criteria,
      "publish_time": datetime.now().isoformat(),
      "close_time": datetime.now().isoformat(),
      "resolve_time": datetime.now().isoformat(),
      "id": 0,  # Dummy ID
      "type": "binary"
  }

  print("\nForecasting...\n")
  try:
    final_result, summarization = await forecast_single_question(
        question_details=question_details,
        cache_seed=42,
        is_multiple_choice=False,
        options=None,
        news=user_news
    )
  except Exception as e:
    print("An error occurred during the forecasting process.")
    print(f"Error details: {e}")

  if final_result is not None and summarization is not None:
    print("\n--- Forecast Output ---")
    # Assuming final_result for binary is a percentage. Adjust if it's different.
    if isinstance(final_result, (float, int)):
      print(f"Final Forecast Probability: {final_result}%")
    else: # Placeholder for other types, like dict for multiple choice
      print(f"Final Forecast: {final_result}")
    
    print("\n--- Analysis Summary ---")
    print(summarization)
  else:
    print("\nForecasting could not be completed due to an error.")

if __name__ == "__main__":
  print("Welcome to the AI Forecasting Applet!")
  print("This tool uses AI to forecast the probability of an event based on your input.")
  print("--------------------------------------------------------------------------")
  
  dotenv.load_dotenv()
  api_key = os.getenv("OPENAI_API_KEY")

  if not api_key:
    print("\nError: OPENAI_API_KEY not found in environment variables.")
    print("Please set it in your .env file or as an environment variable for the applet to function.")
  else:
    print("\nOPENAI_API_KEY loaded successfully.")
    
    user_question = get_user_question()
    user_resolution_criteria = get_resolution_criteria()
    user_news = get_user_news()

    asyncio.run(run_forecast(user_question, user_resolution_criteria, user_news))
