from app.db_snowflake import get_snowflake_connection

def insert_into_snowflake(row: dict):
    query = """
        INSERT INTO SNOWFLAKE_LEARNING_DB.PUBLIC.PROVIDER_DETAILS (
            NPI,
            SPECIALITY,
            PROVIDER_ORGANIZATION_NAME,
            PROVIDER_LASTNAME,
            PROVIDER_FIRSTNAME,
            PROVIDER_MIDDLENAME,
            EMPLOYER_IDENTIFICATION_NUMBER,
            PROVIDER_ADDRESS,
            PROVIDER_CITY_NAME,
            PROVIDER_STATE_NAME,
            PROVIDER_POSTALCODE
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    params = (
        row["NPI"],
        row["SPECIALITY"],
        row["PROVIDER_ORGANIZATION_NAME"],
        row["PROVIDER_LASTNAME"],
        row["PROVIDER_FIRSTNAME"],
        row["PROVIDER_MIDDLENAME"],
        row["EMPLOYER_IDENTIFICATION_NUMBER"],
        row["PROVIDER_ADDRESS"],
        row["PROVIDER_CITY_NAME"],
        row["PROVIDER_STATE_NAME"],
        row["PROVIDER_POSTALCODE"]
    )

    conn = get_snowflake_connection()
    cur = conn.cursor()

    cur.execute(query, params)
    conn.commit()

    cur.close()
    conn.close()
