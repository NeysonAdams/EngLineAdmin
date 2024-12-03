from config import GPT_KEY
from openai import OpenAI
import os

api_key = GPT_KEY

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
    prompt = f"""
     Question: {question}
    Answer: {user_answer}

    Read the text and evaluate the answer to the question based on two criteria:
    1. Logical correctness: Check if the answer logically follows from the question and correctly addresses the question.


    Return a JSON object with the following structure:
    {{
        "correct": bool variable shows if answer is correct
        "description": if answer is not correct show right answer on {language} 
    }}
    """
    response = ask_gpt(prompt)
    return response

def check_text_question(text, question, answer, language):
    prompt = f"""
    Text: {text}
    Question: {question}
    Answer: {answer}

    Read the text and evaluate the answer to the question based on two criteria:
    1. Logical correctness: Check if the answer logically follows from the text and correctly addresses the question.
    2. Grammar correctness: Check if the answer is grammatically correct.

    If the answer is logically correct, but contains grammatical errors, still consider the answer correct but return the grammatical errors.

    Return a JSON object with the following structure:
    {{
        "correct": boolean,  // true if the answer is logically correct, false if not
        "description": string,  // If the answer is incorrect, provide the correct answer in {language}. If the answer is correct, leave this field empty or null.
        "errors": [  // Array of grammatical or contextual errors, if any
            {{
                "answer_text": string,  // The excerpt from the answer with an error
                "correct": string  // The corrected version of the excerpt
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

def chat_start(topic, scenario, user_name):
    prompt = f"""
    Generate a welcome message for a chat based on the following details: 
    topic is '{topic}', 
    scenario is '{scenario}', 
    and the user's name is '{user_name}'. 
    The message should be strictly in English and align with the topic and scenario. 
    Return the result in the following JSON format:
    {{
        'message': 'Generated message here'
    }}
    """

    response = ask_gpt(prompt)
    return response

def chat_answer(topic, scenario, user_name, data, message):
    prompt = f"""
        Generate an answer message for a chat based on the following details: 
        the topic is '{topic}', 
        the scenario is '{scenario}', 
        the user's name is '{user_name}', 
        all chat messages are: {data}, 
        and the user's last message is: '{message}'. 
        The generated message should be strictly in English, align with the topic and scenario, 
        and serve as an answer to the user's last message. 
        If the user's message contains an error, 
        the response should start with 'I am sorry but...' followed by the correction,
        and then proceed to answer the user's question. Return the result in the following JSON format:
        {{
            'message': 'Generated message here',
        }}
        """

def generate_test_question(difficulty, language):
    prompt = read_prompt('test_question_prompt.txt')

    response = ask_gpt(prompt)
    return response

def generate_audio_question(difficulty, language):
    prompt = read_prompt('audio_question_prompt.txt')


    response = ask_gpt(prompt)
    return response

def generate_text_question(difficulty, language, type):
    prompt = read_prompt('input_question_prompt.txt')

    response = ask_gpt(prompt)
    return response

def generate_word_pair(difficulty, type):
    prompt = read_prompt('word_pair_prompt.txt')

    response = ask_gpt(prompt)
    return response

promt_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'prompt'))

def read_prompt(file):
    # Указываем путь к файлу
    file_path = promt_folder+"/"+file

    # Читаем содержимое файла
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # Сохраняем текст в переменную
    prompt_text = file_content

    # Просто для демонстрации возвращаем содержимое файла
    return prompt_text

def save_prompt(file, prompt):
    file_path = promt_folder + "/"+file
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(prompt)