from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    SNOW_USER: str = os.getenv("SNOW_USER")
    SNOW_PASSWORD: str = os.getenv("SNOW_PASSWORD")
    SNOW_ACCOUNT: str = os.getenv("SNOW_ACCOUNT")
    SNOW_WAREHOUSE: str = os.getenv("SNOW_WAREHOUSE", "COMPUTE_WH")
    SNOW_DATABASE: str = os.getenv("SNOW_DATABASE")
    SNOW_SCHEMA: str = os.getenv("SNOW_SCHEMA")
    SNOW_ROLE: str = os.getenv("SNOW_ROLE")

settings = Settings()