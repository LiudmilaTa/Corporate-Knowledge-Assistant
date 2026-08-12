import os
from dotenv import load_dotenv

load_dotenv()

print("HOST:", os.getenv("POSTGRES_HOST"))
print("PORT:", os.getenv("POSTGRES_PORT"))
print("DB:", os.getenv("POSTGRES_DB"))
print("USER:", os.getenv("POSTGRES_USER"))
print("PASSWORD:", os.getenv("POSTGRES_PASSWORD"))
