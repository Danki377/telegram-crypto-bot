import os
import json
import time
import telegram

# 🚀 Configuration
TELEGRAM_BOT_TOKEN = "8136039108:AAF2v9-ABubJJOQtZsC3EfHcFmjPUridDoM"
CHAT_ID = "5171530791"
SEARCH_QUERY = "new crypto launch since:2025-01-01"
CHECK_INTERVAL = 300  # Vérifier toutes les 60 secondes

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# 📂 Fonction pour éviter les doublons
LOG_FILE = "logs.txt"

def is_already_sent(tweet_id):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, "r") as file:
        return str(tweet_id) in file.read()

def save_tweet_id(tweet_id):
    with open(LOG_FILE, "a") as file:
        file.write(str(tweet_id) + "\n")

# 🔄 Boucle infinie pour surveiller Twitter
while True:
    print("🔍 Recherche de nouveaux tweets...")
    
    # Exécuter snscrape et récupérer les résultats
    tweets = os.popen(f"snscrape --jsonl twitter-search '{SEARCH_QUERY}'").read()
    tweets_data = [json.loads(tweet) for tweet in tweets.splitlines()]
    
    # Vérifier chaque tweet
    for tweet in tweets_data:
        tweet_id = tweet["id"]
        tweet_text = tweet["content"]
        tweet_link = f"https://twitter.com/{tweet['user']['username']}/status/{tweet_id}"

        if not is_already_sent(tweet_id):
            message = f"🚀 Nouvelle crypto détectée :\n{tweet_text}\n🔗 {tweet_link}"
            bot.send_message(chat_id=CHAT_ID, text=message)
            save_tweet_id(tweet_id)
            print(f"✅ Tweet envoyé : {tweet_link}")

    print("🕐 Attente avant la prochaine recherche...")
    time.sleep(CHECK_INTERVAL)  # Attendre avant de recommencer
