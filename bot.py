import os
import json
import random
import time
import tweepy

STATE_FILE = "state.json"
TWEETS_FILE = "tweets.json"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    api_key = os.environ["X_API_KEY"].strip()
    api_secret = os.environ["X_API_SECRET"].strip()
    access_token = os.environ["X_ACCESS_TOKEN"].strip()
    access_secret = os.environ["X_ACCESS_SECRET"].strip()

    print(f"Key uzunluklari -> API_KEY:{len(api_key)}, API_SECRET:{len(api_secret)}, ACCESS_TOKEN:{len(access_token)}, ACCESS_SECRET:{len(access_secret)}")

    tweets = load_json(TWEETS_FILE, [])
    if not tweets:
        print("Hata: tweets.json bos.")
        return

    state = load_json(STATE_FILE, {"posted_indices": []})
    posted = set(state.get("posted_indices", []))
    available_indices = [i for i in range(len(tweets)) if i not in posted]

    if not available_indices:
        posted = set()
        available_indices = list(range(len(tweets)))

    chosen_idx = random.choice(available_indices)
    tweet_text = tweets[chosen_idx]

    if os.environ.get("SKIP_JITTER") != "true":
        delay = random.randint(60, 900)
        print(f"Organik zamanlama icin {delay} saniye bekleniyor...")
        time.sleep(delay)

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )

    try:
        me = client.get_me(user_auth=True)
        print(f"Baglanilan Hesap: @{me.data.username}")
        response = client.create_tweet(text=tweet_text)
        print(f"Tweet basariyla gonderildi! ID: {response.data['id']}")
        posted.add(chosen_idx)
        save_json(STATE_FILE, {"posted_indices": sorted(list(posted))})
    except tweepy.TweepyException as e:
        print("X API Detayli Hata:", e)
        if hasattr(e, "response") and e.response is not None:
            print("Sunucu Yaniti:", e.response.text)
        raise

if __name__ == "__main__":
    main()
