import tweepy
import requests
import os
from time import sleep
from datetime import datetime

# Configuration via variables d'environnement (Replit Secrets)
TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET = os.environ['TWITTER_API_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# Mots-clés à surveiller
KEYWORDS = ["bon plan", "promo", "#crypto"]
seen_tweets = set() # Anti-doublons

def send_telegram_alert(text, author, url):
"""Envoi de la notification Telegram"""
message = (
f"🔔 **Nouveau Tweet**\n\n"
f"👤 Auteur: @{author}\n"
f"📝 Texte: {text}\n\n"
f"🔗 {url}"
)
requests.post(
f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
)

def check_tweets():
"""Vérification des nouveaux tweets"""
auth = tweepy.OAuth1UserHandler(
TWITTER_API_KEY, TWITTER_API_SECRET,
TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)
api = tweepy.API(auth)
for keyword in KEYWORDS:
tweets = api.search_tweets(q=keyword, count=5, tweet_mode="extended")
for tweet in tweets:
tweet_id = tweet.id_str
if tweet_id not in seen_tweets:
seen_tweets.add(tweet_id)
tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet_id}"
send_telegram_alert(tweet.full_text, tweet.user.screen_name, tweet_url)

# Boucle principale
if __name__ == "__main__":
print(f"{datetime.now()} → Bot démarré. Surveillance des mots-clés : {KEYWORDS}")
while True:
check_tweets()
sleep(300) # Vérifie toutes les 5 minutes
