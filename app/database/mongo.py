from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["allergy_detector"]

allergen_collection = db["allergens"]
scan_collection = db["scans"]
