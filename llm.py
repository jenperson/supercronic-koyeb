from dotenv import load_dotenv
from openai import OpenAI
import os
from transformers import AutoTokenizer
import re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

GPT_OSS_20B_API_URL = os.getenv("GPT_OSS_20B_API_URL")


class GptOpenAi:
    """
    Use the model served from Koyeb
    """
    def __init__(self, api_url: str = f"{GPT_OSS_20B_API_URL}", model: str = "openai/gpt-oss-20b"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_url,
        )
        self.model = model

    def ask(self, formatted_input: str, temperature: float = 1.0,  max_tokens: int = 500, role: str = "user"):
        """Send a request to the OpenAI API and return the response."""
        if not isinstance(formatted_input, str):
            formatted_input = formatted_input.to_string()

        try:
            messages=[{"role": role, "content": formatted_input}]
            response = self.client.chat.completions.create(
                messages=messages,
                model=f"/models/{self.model}",
                # max_tokens=max_tokens,
                # temperature=temperature
            )

            return response.choices[0].text if response.choices else None
        except Exception as e:
            print(f"Request failed: {e}")
            return None
        
    def askNoChat(self, formatted_input: str, temperature: float = 1.0,  max_tokens: int = 500, role: str = "user"):
        instructions = (
            "You are ChatGPT. Given a set of stories, create a summary message explaining the stories as though you were speaking to a friend."
            "Include the links to all the stories if present, or just the info from the text if present." 
            "Respond in no more than 500 characters. Skip unnecessary explanation. Only include the final summary in plain text"
        )
        tokenizer = AutoTokenizer.from_pretrained("openai/gpt-oss-20b", trust_remote_code=True)
        """Send a request to the OpenAI API and return the response."""
        if not isinstance(formatted_input, str):
            formatted_input = formatted_input.to_string()

        try:
            messages=[{"role": "system", "content": instructions},{"role": role, "content": formatted_input}]
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            response = self.client.completions.create(
                prompt=prompt,
                model=f"/models/{self.model}",
                max_tokens=max_tokens,
                temperature=temperature
            )

            if response.choices:
                print(response.choices)
                chat_response = response.choices[0].text
                match = re.search(r'final(.*)', chat_response)
                print(match)
            return match.group(1).replace("\n", "").strip() if match else None
        except Exception as e:
            print(f"Request failed: {e}")
            return None
