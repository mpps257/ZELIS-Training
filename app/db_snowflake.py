import snowflake.connector
from app.config import settings

def get_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=settings.SNOW_USER,
            password=settings.SNOW_PASSWORD,
            account=settings.SNOW_ACCOUNT,
            warehouse=settings.SNOW_WAREHOUSE,
            database=settings.SNOW_DATABASE,
            schema=settings.SNOW_SCHEMA,
            role=settings.SNOW_ROLE
        )
        print("Snowflake connection SUCCESS")
        return conn

    except Exception as e:
        print("Snowflake connection FAILED:", str(e))
        raise
