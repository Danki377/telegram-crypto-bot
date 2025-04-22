import tweepy
import requests
import os
import time
import json
import random
from datetime import datetime
from calendar import monthrange

# Configuration API Twitter v2
BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Configuration Telegram
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Paramètres de recherche
QUERY = '''
("new cryptocurrency" OR 
"token launch" OR 
"new coin announced" OR 
"crypto presale" OR 
"new crypto") lang:en -is:retweet -is:reply
'''

class ApiManager:
    def __init__(self):
        self.MAX_MONTHLY_REQUESTS = 100
        self.MIN_RESULTS = 10
        self.usage_file = "twitter_usage.json"
        self.current_month = datetime.now().month
        self.used_requests = 0
        self.load_usage()

    def load_usage(self):
        try:
            with open(self.usage_file, 'r') as f:
                data = json.load(f)
                if data['month'] == self.current_month:
                    self.used_requests = data['count']
        except:
            self.used_requests = 0

    def save_usage(self):
        with open(self.usage_file, 'w') as f:
            json.dump({
                'month': self.current_month,
                'count': self.used_requests
            }, f)

    def remaining_requests(self):
        return self.MAX_MONTHLY_REQUESTS - self.used_requests

    def calculate_delay(self):
        now = datetime.now()
        total_days = monthrange(now.year, now.month)[1]
        days_elapsed = now.day - 1
        
        ideal_daily = self.MAX_MONTHLY_REQUESTS / total_days
        max_daily = min(ideal_daily * 2, 10)
        remaining_today = max(max_daily - (self.used_requests / (days_elapsed + 1)), 0.1)
        
        base_delay = 86400 / remaining_today
        return max(base_delay * random.uniform(0.7, 1.3), 3600)

    def make_request(self):
        if self.used_requests >= self.MAX_MONTHLY_REQUESTS:
            return None
            
        try:
            response = client.search_recent_tweets(
                query=QUERY,
                max_results=self.MIN_RESULTS,
                tweet_fields=["author_id","created_at"],
                user_fields=["username","verified","followers_count"],
                expansions="author_id"
            )
            self.used_requests += 1
            self.save_usage()
            return response
        except tweepy.TweepyException as e:
            print(f"Erreur API: {str(e)[:100]}")
            return None

api_manager = ApiManager()

def send_alert(text, author, url):
    try:
        message = f"""🚨 **Nouveau Projet Crypto**
        
👤 Source: @{author}
📝 {text[:150]}...

🔗 {url}"""
        
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            },
            timeout=3
        )
    except Exception as e:
        print(f"Erreur Telegram: {str(e)[:100]}")

def process_response(response):
    if not response or not response.data:
        return []
        
    users = {u.id: u for u in response.includes.get('users', [])}
    valid_tweets = []
    
    sorted_tweets = sorted(
        response.data,
        key=lambda t: users.get(t.author_id).followers_count if users.get(t.author_id) else 0,
        reverse=True
    )[:5]
    
    for tweet in sorted_tweets:
        author = users.get(tweet.author_id)
        if author and author.verified:
            tweet_url = f"https://twitter.com/{author.username}/status/{tweet.id}"
            valid_tweets.append((tweet.text, author.username, tweet_url))
    
    return valid_tweets

if __name__ == "__main__":
    print(f"[Démarrage] Requêtes disponibles ce mois: {api_manager.remaining_requests()}")
    
    while True:
        delay = api_manager.calculate_delay()
        print(f"Prochaine requête dans {delay/3600:.2f} heures")
        time.sleep(delay)
        
        response = api_manager.make_request()
        
        if response:
            tweets = process_response(response)
            for text, author, url in tweets:
                send_alert(text, author, url)
                time.sleep(random.uniform(2, 5))
                
            print(f"Tweets trouvés: {len(tweets)} | Requêtes utilisées: {api_manager.used_requests}/100")

