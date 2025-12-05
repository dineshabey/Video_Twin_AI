import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

with open("available_models.txt", "w") as f:
    for m in genai.list_models():
        f.write(f"Name: {m.name}\n")
        f.write(f"Supported generation methods: {m.supported_generation_methods}\n")
        f.write("-" * 20 + "\n")
print("Models listed in available_models.txt")
