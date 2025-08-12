from dotenv import load_dotenv
from openai import OpenAI
import os
from transformers import AutoTokenizer
import re

load_dotenv()
GPT_OSS_20B_API_URL = os.getenv('GPT_OSS_20B_API_URL')

class GptOpenAi:

    # Use the model served from Koyeb
    def __init__(self, api_url: str = f'{GPT_OSS_20B_API_URL}', model: str = 'openai/gpt-oss-20b'):
        self.client = OpenAI(
            api_key=None,
            base_url=api_url,
        )
        self.model = model

    # Uses the chat completions function to create a response.
    def ask(self, formatted_input: str, temperature: float = 1.0,  max_tokens: int = 500, role: str = 'user'):
        # Send a request to the OpenAI API and return the response.
        if not isinstance(formatted_input, str):
            formatted_input = formatted_input.to_string()

        try:
            messages=[{'role': role, 'content': formatted_input}]
            response = self.client.chat.completions.create(
                messages=messages,
                model=f'/models/{self.model}',
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.choices[0].text if response.choices else None
        except Exception as e:
            print(f'Request failed: {e}')
            return None
        
    # Uses the completions function to create a response
    def askNoChat(self, formatted_input: str, temperature: float = 1.0,  max_tokens: int = 500, role: str = 'user'):
        instructions = (
            'You are ChatGPT. Given a set of stories, create a summary message explaining the stories as though you were speaking to a friend.'
            'Include the links to all the stories if present, or just the info from the text if present.' 
        )
        tokenizer = AutoTokenizer.from_pretrained('openai/gpt-oss-20b', trust_remote_code=True)
        # Send a request to the OpenAI API and return the response.
        if not isinstance(formatted_input, str):
            formatted_input = formatted_input.to_string()

        try:
            messages=[{'role': 'system', 'content': instructions},{'role': role, 'content': formatted_input}]
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            response = self.client.completions.create(
                prompt=prompt,
                model=f'/models/{self.model}',
                max_tokens=max_tokens,
                temperature=temperature
            )

            if response.choices:
                chat_response = response.choices[0].text
                match = re.search(r'final(.*)', chat_response, re.DOTALL)
                # Remove newlines
                final_result = match.group(1).replace(r'\\n', ' ').replace('\\', '').strip()
                # Remove markdown formatting from URLs
                final_result = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'\1: \2', final_result)
                return final_result if final_result else None
        except Exception as e:
            print(f'Request failed: {e}')
            return None
