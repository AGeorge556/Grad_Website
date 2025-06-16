import os
import requests
import json as pyjson
from google.generativeai import GenerativeModel, configure

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
configure(api_key=GEMINI_API_KEY)

def get_gemini_model():
    return GenerativeModel('gemini-pro')

def gemini_generate_flashcards(summary: str, max_flashcards: int = 5):
    model = get_gemini_model()
    prompt = (
        f"You are an expert educator. Based on the following summary, generate {max_flashcards} high-quality flashcards. "
        "Each flashcard should be a JSON object with 'question' and 'answer' fields. "
        "Questions should be clear, concise, and test key concepts. Answers should be accurate and complete. "
        "Return ONLY a JSON array of objects, no extra text. Example: "
        "[{'question': 'What is X?', 'answer': 'X is ...'}, ...]"
        f"\nSummary: {summary}"
    )
    try:
        response = model.generate_content(prompt)
        text = response.text
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end != -1:
            arr = pyjson.loads(text[start:end])
            # Post-process: filter for valid flashcards
            valid = [
                f for f in arr
                if isinstance(f, dict) and 'question' in f and 'answer' in f and f['question'] and f['answer']
            ]
            return valid[:max_flashcards]
        return []
    except Exception as e:
        print(f"Gemini flashcard parse error: {e}")
        return []

def gemini_generate_quizzes(summary: str, max_questions: int = 5):
    model = get_gemini_model()
    prompt = (
        f"You are an expert educator. Based on the following summary, generate {max_questions} multiple-choice quiz questions. "
        "Each question should be a JSON object with: 'question' (string), 'options' (array of 4 strings), and 'correctAnswer' (index 0-3 of the correct option). "
        "Questions should test understanding of key concepts. Return ONLY a JSON array of objects, no extra text. Example: "
        "[{'question': 'What is X?', 'options': ['A', 'B', 'C', 'D'], 'correctAnswer': 2}, ...]"
        f"\nSummary: {summary}"
    )
    try:
        response = model.generate_content(prompt)
        text = response.text
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end != -1:
            arr = pyjson.loads(text[start:end])
            # Post-process: filter for valid quizzes
            valid = [
                q for q in arr
                if (
                    isinstance(q, dict)
                    and 'question' in q and isinstance(q['question'], str) and q['question']
                    and 'options' in q and isinstance(q['options'], list) and len(q['options']) == 4
                    and all(isinstance(opt, str) and opt for opt in q['options'])
                    and 'correctAnswer' in q and isinstance(q['correctAnswer'], int)
                    and 0 <= q['correctAnswer'] < 4
                )
            ]
            return valid[:max_questions]
        return []
    except Exception as e:
        print(f"Gemini quiz parse error: {e}")
        return []

def gemini_video_chat(summary: str, user_message: str):
    model = get_gemini_model()
    prompt = f"Given this summary: {summary}\nAnswer the following question as an AI tutor: {user_message}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini chat parse error: {e}")
        return "Sorry, I couldn't answer that question right now." 