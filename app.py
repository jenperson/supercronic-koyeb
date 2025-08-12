from twilio.rest import Client
import os
from hacker_news import HackerNews
from llm import GptOpenAi

# Your Account SID and Auth Token from console.twilio.com stored as envars in Koyeb
account_sid = os.environ.get('TWILIO_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

# Your WhatsApp number at which you will receive the messages
whatsapp_to = os.environ.get('WHATSAPP_TO')

# Find the "from" phone number in the Twilio console
whatsapp_from = os.environ.get('WHATSAPP_FROM')

client = Client(account_sid, auth_token)
llm = GptOpenAi()
hacker_news = HackerNews()

# Get the ten top stories
top_stories = hacker_news.load_top_stories_concurrent()
# Have gpt-oss-20b summarize the stories
top_summary = llm.summarize_hn(f'{top_stories}', max_tokens=4000)

# Send messages to your WhatsApp number
def send_whatsapp_message_in_chunks(body, chunk_size=1600):
    # Split gpt-oss-20b response into 1600 char chunks to meet the delivery limits of WhatsApp with Twilio
    part_num = 1

    while body:
        if len(body) > chunk_size:
            split_point = body.rfind(' ', 0, chunk_size)
            if split_point == -1:
                split_point = chunk_size
        else:
            split_point = len(body)  # final chunk size or smaller

        part = body[:split_point]
        body = body[split_point:].lstrip()

        # Send the chunk
        message = client.messages.create(
            to=f'whatsapp:{whatsapp_to}',
            from_=f'whatsapp:{whatsapp_from}',
            body=part
        )
        print(f'Sent part {part_num} SID: {message.sid}')
        part_num += 1

messages = send_whatsapp_message_in_chunks(top_summary)