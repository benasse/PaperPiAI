import os
import requests
import random
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Charger les variables depuis .env (ou l'environnement)
load_dotenv()

IMMICH_URL = os.getenv("IMMICH_URL", "https://exemple.immich.app")
API_KEY = os.getenv("API_KEY", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
_persons = os.getenv("PERSON_IDS", "aaaaaaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
PERSON_IDS = [p.strip() for p in _persons.split(",") if p.strip()]

os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {"x-api-key": API_KEY}

# 1️⃣ Choisir une personne au hasard
person_id = random.choice(PERSON_IDS)

# 2️⃣ Récupérer le nombre total d'assets pour cette personne
stats_url = f"{IMMICH_URL}/api/people/{person_id}/statistics"
resp = requests.get(stats_url, headers=headers)
resp.raise_for_status()
total_assets = resp.json().get("assets", 0)

if total_assets == 0:
    print(f"No assets found for person {person_id}")
    exit(1)

# 3️⃣ Choisir un index aléatoire
random_index = random.randint(0, total_assets - 1)

# 4️⃣ Récupérer l'asset
search_url = f"{IMMICH_URL}/api/search/metadata"
payload = {
    "type": "IMAGE",
    "page": random_index + 1,  # pages start at 1
    "size": 1,
    "personIds": [person_id]
}
resp = requests.post(search_url, headers=headers, json=payload)
resp.raise_for_status()
items = resp.json().get("assets", {}).get("items", [])

if not items:
    print("No image found at the selected index")
    exit(1)

asset = items[0]
file_url = f"{IMMICH_URL}/api/assets/{asset['id']}/original"

# 5️⃣ Télécharger l'image
resp = requests.get(file_url, headers=headers)
resp.raise_for_status()

img = Image.open(BytesIO(resp.content))

# 6️⃣ Sauver l'image localement
filename = os.path.join(OUTPUT_DIR, f"{asset['id']}.jpg")
img.save(filename)
print(f"Downloaded random image for person {person_id} -> {filename}")
