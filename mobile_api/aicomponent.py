import os.path

from openai import OpenAI

api_key = ""

client = OpenAI(
    # This is the default and can be omitted
    api_key=api_key,
)

def text_to_speach(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    return response

def speach_to_text(audio_file):
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return transcription.text

def ask_gpt(prompt):
    return client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user",
             "content": prompt}
        ]
    )

def check_answer(question, user_answer, language):
    # Формулируем запрос к GPT-3 для проверки правильности ответа
    prompt = f"""
    Question: {question}\nAnswer: {user_answer}\nIs the answer correct?
    return json array:
    {{
        "correct": bool variable shows if answer is correct
        "description": if answer is not correct show right answer on {language} 
    }}
    """
    response = ask_gpt(prompt)
    return response

def check_text_question(text, questoion, answer, language):
    prompt = f"""
    Text : {text}
    Question: {questoion}
    Answer: {answer}
    Read the text and check the answer on the question.
    return json array:
    {{
        "correct": bool variable shows if answer is correct,
        "description": if answer is not correct show right answer on {language}
        "errors": [ array of grammar or context errors
            {{
                "answer_text": excerpt from the answer,
                "correct": correct example of translation
            }}
            ...
        ]
    }}
    """
    response = ask_gpt(prompt)
    return response
def generate_text(level, w_length, topic="any"):
    prompt = f"""
    Generate a text of {w_length} words with the text complexity of {level} on {topic} topic
    return json array:
    {{
        "original_text": Generated text on english language
        "level": complexity of text ['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced']
        "topic": {topic}
    }}
    """
    response = ask_gpt(prompt)
    return response

def check_translation(text, translation):
    prompt = f"""
    Check translation of text : 
    Original Text : {text}
    Translation: {translation}
    Return JSON Array with name 
    {{
        "percentage_translated":  how many percent of text has been translated,
        "errors": [
            {{
                "original_text": excerpt from the original text,
                "user_translation": excerpt from the translation
                "correct": correct example of translation
            }}
            ...
        ],
        "warnings": [ this is examples of better translation
            {{
                "original_text": excerpt from the original text,
                "user_translation": excerpt from the translation
                "better_translation": better example of translation
            }}
            ...
        ]
    }}
    Each excerpt have to contain 3-6 words. 
    Each excerpt have to start and finish with '...' signs
    If any word has translated uncorrect THIS IS ERROR
    """
    response = ask_gpt(prompt)
    return response

def check_grammar(text, language):
    prompt = f"""
    Check grammar of the text
    Original Text : {text}
    return json array with grammar errors:
     {{
        "errors" : [
            {{
                "original_text" : excerpt from the original text,
                "correct": correct variant of tne excerpt,
                "description" : brif description of error and right grammar rule  on {language} language
            }}
            ...
        ]
    }}
    Only Grammar Error have to be in this array.
    Each excerpt have to contain 3-6 words. 
    Each excerpt have to start and finish with '...' signs
    If Error means that word is missing this word have to be among of <color=#009D30> </color> tag only in "correct" field
    If You not found any error in text return empty "errors" array
    """
    response = ask_gpt(prompt)
    return response


