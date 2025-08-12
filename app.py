from twilio.rest import Client
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.utils import quote
from llm import GptOpenAi

# Your Account SID and Auth Token from console.twilio.com stored as envars in Koyeb
account_sid = os.environ.get('TWILLIO_SID')
auth_token = os.environ.get('TWILLIO_AUTH_TOKEN')
whatsapp_to = os.environ.get('WHATSAPP_TO')
whatsapp_from = os.environ.get('WHATSAPP_FROM')
client = Client(account_sid, auth_token)
llm = GptOpenAi()

hn_base_url = 'https://hacker-news.firebaseio.com/v0/'
endpoint_suffix = '.json'

# Get an array of IDs of the top stories from Hacker News
def get_top_stories():
    order_by_value = quote('$key', safe='$')
    try:
        response = requests.get(f'{hn_base_url}topstories{endpoint_suffix}/?limitToFirst={10}&orderBy="{order_by_value}"')
        response.raise_for_status()
        data = response.json() 
        print('Get Top Stories API Response:', data)
        return data
    except requests.exceptions.RequestException as e:
        print('Error calling Top Stores API:', e)

# Get story information for a given story ID
def get_story_by_id(item_id: str):
    try:
        response = requests.get(f'{hn_base_url}item/{item_id}{endpoint_suffix}')
        response.raise_for_status()
        data = response.json()
        print('Get Story API Response:', data)
        return data
    except requests.exceptions.RequestException as e:
        print('Error calling Item ID API:', e)

# Get user information for the story or comment poster by ID
def get_user(user_id: str):
    try:
        response = requests.get(f'{hn_base_url}user/{user_id}{endpoint_suffix}')
        response.raise_for_status() 
        data = response.json()
        print('Get Story API Response:', data)
        return data
    except requests.exceptions.RequestException as e:
        print('Error calling Story API:', e)

# Build array of top stories
def load_top_stories_concurrent():
    top_story_ids = get_top_stories()
    results = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_id = {executor.submit(get_story_by_id, str(story_id)): story_id for story_id in top_story_ids}

        for future in as_completed(future_to_id):
            story_id = future_to_id[future]
            try:
                story_data = future.result()
                if story_data:
                    story = {
                        'title': story_data.get('title', None),
                        'text': story_data.get('text', None),
                        'url': story_data.get('url', None)
                    }
                    results.append(story)
            except Exception as e:
                print(f'Exception fetching story {story_id}: {e}')

    return results

top_stories = load_top_stories_concurrent()
top_summary = llm.askNoChat(f'{top_stories}')
message = client.messages.create(
    to=f'whatsapp:{whatsapp_to}',
    from_=f'whatsapp:{whatsapp_from}',
    body=top_summary
)

print(message.sid)