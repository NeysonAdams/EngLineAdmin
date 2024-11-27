from config import GPT_KEY
from openai import OpenAI

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
    prompt = f"""
        Generate test question with 4 variant of answer
        One variant is true, 3 is wrong
        topics of the question: English grammar, choose missing word,   
        the difficulty of question is {difficulty}
        the language of question{language}
        Return the result in the following JSON format:
        {{
            'question': question of the test. Language of thr quest is {language},
            'var1': First variant of answer,
            'var2': Second variant of answer,
            'var3': Threed variant of answer,
            'var4': Four variant of answer,
            'right': the number of right variant of answer ( can be 1, 2, 3, 4)
            
        }}
    """

    response = ask_gpt(prompt)
    return response

def generate_audio_question(difficulty, language):
    prompt = f"""
        Generate question with audio
        Type of the question Listen the audio and answer the question
        the difficulty of question is {difficulty}
        the language of question{language}
        Return the result in the following JSON format:
        {{
            'question': question. Language of thr quest is {language}, questions depends from audio
            'audio_query': text of the listening question always in english language only this text will be in audio file
            
        }}
    """

    response = ask_gpt(prompt)
    return response

def generate_text_question(difficulty, language, type):
    prompt = f"""
        Generate questions for a English language learner on a professional topic. The questions should be of the following types:
        
        the difficulty of question is {difficulty}
        type of the question : {type}
        
        check_answer — This is a simple question where the learner provides a written answer. The answer is checked by GPT. 
        Example: "What is the primary function of a database in software development?" 
        language of question dependes from difficulty 
        If difficulty is Beginner Elementary PreIntermidia Intermidia the is {language} otherwise English.
        
        add_missing — The question consists of a sentence with missing words, where each missing character is replaced with _. 
        Example: "A ______ is used to store and manage data." Answer: "database".
        
        check_grammar — This is a grammar question where the answer should be short (2–4 words) and correct the mistake in the sentence. 
        Example: "She go to work every day." Answer: "She goes".
        
        Please create three questions on the topic of [insert topic, e.g., "basics of programming"], one of each type. 
        Format the questions and answers clearly.
        Return the result in the following JSON format:
        {{
            'question': generated question,
            'answer': answer on this question (according add_missing type write answer  separated by commas Example: "A ______ is used to _____ and manage data." Answer: "database, store")
        }}
        WARNING ITS ABSOLUTELY IMPOSSIBLE TO RETURN ARRAY! ONLY ONE QUESTION AND ONE ANSWER WHICH FOLLOWING THE TYPE {type}
    """

    response = ask_gpt(prompt)
    return response

def generate_word_pair(difficulty, type):
    prompt = f"""
        Generate Array words pairs for a English language learner on a professional topic. The questions should be of the following types:
        
        the difficulty is {difficulty}
        type of the question {type}
        
        if type is 'translate' Return the result in the following JSON format:
        {{
            'words': generate 5-8 length array
            [
                {{
                    'id' :-1,
                    'eng': word on English,
                    'rus': translation on Russian Language,
                    'uzb': translation on Uzbek Language
                }}
            ]
        }}
        
    """

    response = ask_gpt(prompt)
    return response