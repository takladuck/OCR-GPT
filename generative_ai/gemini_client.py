import google.generativeai as genai
from generative_ai import Api_key

genai.configure(api_key=Api_key.API_KEY)


def generate_content(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
