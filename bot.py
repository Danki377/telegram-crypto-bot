import os
import json
import time
import telegram
import ssl
import requests

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

# 🚨 Désactivation de la vérification SSL pour requests
# Créer un context SSL qui ignore la vérification des certificats
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 🔄 Boucle infinie pour surveiller Twitter
while True:
    print("🔍 Recherche de nouveaux tweets...")

    # Utiliser requests avec un context SSL modifié pour ignorer la vérification SSL
    os.environ["SSL_CERT_FILE"] = "/etc/ssl/certs/ca-certificates.crt"  # Sur certaines machines, spécifiez le fichier de certificats

    # Exécuter snscrape en utilisant un appel système pour contourner l'option SSL
    tweets = os.popen(f"snscrape --jsonl twitter-search '{SEARCH_QUERY}'").read()
    
    # Récupérer les données des tweets
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
