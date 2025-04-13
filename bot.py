import tweepy
import requests
import os
from dotenv import load_dotenv
from time import sleep

# Charge les clés depuis .env
load_dotenv()

# Config Twitter
auth = tweepy.OAuth1UserHandler(
consumer_key=os.getenv("TWITTER_API_KEY"),
consumer_secret=os.getenv("TWITTER_API_SECRET"),
access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
)
twitter_api = tweepy.API(auth)

# Config Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Mots-clés à surveiller (personnalisez cette liste !)
KEYWORDS = ["New coin launching $", "New Official meme launching", "Launching at", "Launching soon"]

# Pour éviter les doublons
seen_tweets = set()

def send_telegram_alert(tweet_text, author, tweet_url):
"""Envoie une notification sur Telegram"""
message = (
f"🔔 **Nouveau Tweet**\n\n"
f"📌 **Auteur**: @{author}\n"
f"📝 **Contenu**: {tweet_text}\n\n"
f"🔗 {tweet_url}"
)
requests.post(
f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
)

def check_tweets():
"""Vérifie les nouveaux tweets"""
for keyword in KEYWORDS:
tweets = twitter_api.search_tweets(q=keyword, count=5, tweet_mode="extended")
for tweet in tweets:
tweet_id = tweet.id_str
if tweet_id not in seen_tweets:
seen_tweets.add(tweet_id)
tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet_id}"
send_telegram_alert(tweet.full_text, tweet.user.screen_name, tweet_url)

# Boucle principale
if __name__ == "__main__":
print("🤖 Bot en marche... (Ctrl+C pour arrêter)")
while True:
check_tweets()
sleep(300) # Vérifie toutes les 5 minutes
