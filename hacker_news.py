import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.utils import quote

class HackerNews:

    def __init__(self, limit=10):
        self.limit = limit
        self.hn_base_url = 'https://hacker-news.firebaseio.com/v0/'
        self.endpoint_suffix = '.json'

    # Get an array of IDs of the top stories from Hacker News
    def get_top_stories(self):
        order_by_value = quote('$key', safe='$')
        try:
            response = requests.get(f'{self.hn_base_url}topstories{self.endpoint_suffix}/?limitToFirst={10}&orderBy="{order_by_value}"')
            response.raise_for_status()
            data = response.json() 
            return data
        except requests.exceptions.RequestException as e:
            print('Error calling Top Stores API:', e)

    # Get story information for a given story ID
    def get_story_by_id(self, item_id: str):
        try:
            response = requests.get(f'{self.hn_base_url}item/{item_id}{self.endpoint_suffix}')
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print('Error calling Item ID API:', e)

    # Build array of top stories
    def load_top_stories_concurrent(self):
        top_story_ids = self.get_top_stories()
        results = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_id = {executor.submit(self.get_story_by_id, str(story_id)): story_id for story_id in top_story_ids}

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