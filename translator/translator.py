import json
import os
import tiktoken
import logging
import time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from random import uniform

# Load .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

client = OpenAI(api_key=api_key)

# Constants
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1024
COST_PER_1K_TOKENS = 0.002  # $0.002 per 1K tokens for gpt-3.5-turbo
MAX_COST_DOLLARS = 9.0  # Set maximum cost to $9 to leave some buffer
MAX_RETRIES = 5  # Maximum number of retries for a failed request

# Supported languages with translations for "hardware," "service," and "app"
LANGUAGES = {
    "Spanish": {"code": "es", "hardware": "hardware", "service": "servicio", "app": "aplicación"},
    "Italian": {"code": "it", "hardware": "hardware", "service": "servizio", "app": "app"},
    "French": {"code": "fr", "hardware": "matériel", "service": "service", "app": "application"},
    "German": {"code": "de", "hardware": "Hardware", "service": "Dienst", "app": "App"},
    "Portuguese": {"code": "pt", "hardware": "hardware", "service": "serviço", "app": "aplicativo"},
    "Russian": {"code": "ru", "hardware": "hardware", "service": "услуга", "app": "приложение"},
    "Hindi": {"code": "hi", "hardware": "हार्डवेयर", "service": "सेवा", "app": "ऐप"},
    "Chinese": {"code": "zh", "hardware": "硬件", "service": "服务", "app": "应用"},
    "Japanese": {"code": "ja", "hardware": "ハードウェア", "service": "サービス", "app": "アプリ"},
    "Arabic": {"code": "ar", "hardware": "الأجهزة", "service": "خدمة", "app": "تطبيق"},
    "Afrikaans": {"code": "af", "hardware": "hardeware", "service": "diens", "app": "app"},
    "Catalan": {"code": "ca", "hardware": "maquinari", "service": "servei", "app": "aplicació"}
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_calls.log'),
        logging.StreamHandler()  # This will log to the terminal
    ]
)

def num_tokens_from_string(string: str, model_name: str) -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(string))

def translate_description(description, type_, language_info, retry_count=0):
    # Use the hardcoded translations for "type"
    translated_type = language_info[type_]

    prompt = f"Translate the following description to {language_info['code']}. Do not translate product names, only the text:\n\n{description}\n\nType: {translated_type}"
    
    messages = [
        {"role": "system", "content": f"You are a translator. Translate the given text from English to {language_info['code']}."},
        {"role": "user", "content": prompt}
    ]

    tokens_estimate = sum(num_tokens_from_string(msg["content"], MODEL) for msg in messages) + MAX_TOKENS

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=MAX_TOKENS
        )
        translation = response.choices[0].message.content.strip()
        
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = prompt_tokens + completion_tokens
        cost = (prompt_tokens + completion_tokens) / 1000 * COST_PER_1K_TOKENS

        logging.info(f"API Call: Tokens used: {prompt_tokens + completion_tokens}, Cost: ${cost:.4f}")
        logging.info(f"Response: {translation}")

        return translation, translated_type, total_tokens, cost
    except Exception as e:
        logging.error(f"Error during translation: {e}")
        if retry_count < MAX_RETRIES:
            retry_delay = 2 ** retry_count + uniform(0, 1)  # Exponential backoff with jitter
            logging.info(f"Retrying in {retry_delay:.2f} seconds...")
            time.sleep(retry_delay)
            return translate_description(description, type_, language_info, retry_count + 1)
        else:
            logging.error(f"Max retries exceeded for description: {description}")
            return description, translated_type, 0, 0

def parallel_translate_descriptions(data, language_info):
    total_tokens = 0
    total_cost = 0
    max_workers = 5  # Reduce the number of workers to prevent hitting the API limit

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(translate_description, item['description'], item['type'], language_info): item for item in data}
        
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                item['description'], item['type'], tokens_used, cost = future.result()
                total_tokens += tokens_used
                total_cost += cost
                logging.info(f"Progress: {len([f for f in future_to_item if f.done()])}/{len(future_to_item)} items processed.")
                if total_cost >= MAX_COST_DOLLARS:
                    logging.warning(f"Maximum cost of ${MAX_COST_DOLLARS} reached. Stopping translations.")
                    break
            except Exception as exc:
                logging.error(f"Generated an exception: {exc}")

    return data, total_tokens, total_cost

def translate_for_all_languages(data):
    with ThreadPoolExecutor(max_workers=len(LANGUAGES)) as executor:
        futures = []
        for language, language_info in LANGUAGES.items():
            futures.append(executor.submit(parallel_translate_descriptions, data, language_info))

        for future in as_completed(futures):
            translated_data, total_tokens, total_cost = future.result()
            language_code = LANGUAGES[list(LANGUAGES.keys())[futures.index(future)]]['code']
            output_filename = f"{language_code}_graveyard.json"

            # Write the output JSON file
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)

            logging.info(f"Translation complete for {language_code}. Total tokens used: {total_tokens}. Total cost: ${total_cost:.2f}")
            print(f"Translation complete for {language_code}. Total tokens used: {total_tokens}. Total cost: ${total_cost:.2f}")
            print(f"Output saved to {output_filename}")

# Read the input JSON file
with open('graveyard.json', 'r') as f:
    data = json.load(f)

# Translate descriptions for all languages in parallel
translate_for_all_languages(data)
