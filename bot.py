import os
import json
import time
import ssl
import requests
from urllib3.exceptions import InsecureRequestWarning
import telegram
from dotenv import load_dotenv

# Désactiver les avertissements SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Ignorer la vérification des certificats SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Charger les variables d'environnement depuis un fichier .env
load_dotenv()

# 🚀 Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SEARCH_QUERY = "new crypto launch since:2025-01-01"
CHECK_INTERVAL = 300  # Vérifier toutes les 300 secondes (5 minutes)

# Initialiser le bot Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# 📂 Fonction pour éviter les doublons
LOG_FILE = "logs.txt"

def is_already_sent(tweet_id):
    """Vérifier si un tweet a déjà été envoyé."""
    try:
        if not os.path.exists(LOG_FILE):
            return False
        with open(LOG_FILE, "r") as file:
            return str(tweet_id) in file.read()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier de log: {e}")
        return False

def save_tweet_id(tweet_id):
    """Sauvegarder l'ID du tweet dans le fichier de log pour éviter les doublons."""
    try:
        with open(LOG_FILE, "a") as file:
            file.write(str(tweet_id) + "\n")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier de log: {e}")

# 🔄 Boucle infinie pour surveiller Twitter
while True:
    try:
        print("🔍 Recherche de nouveaux tweets...")
        
        # Exécuter snscrape et récupérer les résultats
        tweets = os.popen(f"snscrape --jsonl twitter-search '{SEARCH_QUERY}'").read()
        tweets_data = [json.loads(tweet) for tweet in tweets.splitlines()]

        # Vérifier chaque tweet
        for tweet in tweets_data:
            tweet_id = tweet["id"]
            tweet_text = tweet["content"]
            tweet_link = f"https://twitter.com/{tweet['user']['username']}/status/{tweet_id}"

            # Vérifier si le tweet a déjà été envoyé
            if not is_already_sent(tweet_id):
                message = f"🚀 Nouvelle crypto détectée :\n{tweet_text}\n🔗 {tweet_link}"
                
                # Envoyer le message Telegram
                try:
                    bot.send_message(chat_id=CHAT_ID, text=message)
                    save_tweet_id(tweet_id)
                    print(f"✅ Tweet envoyé : {tweet_link}")
                except Exception as e:
                    print(f"Erreur lors de l'envoi du message Telegram: {e}")
            else:
                print(f"Tweet déjà envoyé : {tweet_link}")

        print("🕐 Attente avant la prochaine recherche...")
        time.sleep(CHECK_INTERVAL)  # Attendre avant de recommencer
    except Exception as e:
        print(f"Erreur dans le processus de scrapping ou d'envoi: {e}")
        time.sleep(CHECK_INTERVAL)  # Attente avant la prochaine tentative en cas d'erreur
