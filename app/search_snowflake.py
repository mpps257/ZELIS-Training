from app.db_snowflake import get_snowflake_connection

def search_by_npi(npi: str):
    query = """
        SELECT *
        FROM SNOWFLAKE_LEARNING_DB.PUBLIC.PROVIDER_DETAILS
        WHERE NPI = %s
        LIMIT 1;
    """

    conn = get_snowflake_connection()
    cur = conn.cursor()

    cur.execute(query, (npi,))
    rows = cur.fetchall()
    columns = [c[0] for c in cur.description]

    cur.close()
    conn.close()

    if not rows:
        return None

    return dict(zip(columns, rows[0]))

def search_by_filters(first=None, last=None, city=None, state=None):
    query = """
        SELECT *
        FROM SNOWFLAKE_LEARNING_DB.PUBLIC.PROVIDER_DETAILS
        WHERE 1 = 1
    """

    params = []

    if first:
        query += " AND UPPER(PROVIDER_FIRSTNAME) = UPPER(%s)"
        params.append(first)

    if last:
        query += " AND UPPER(PROVIDER_LASTNAME) = UPPER(%s)"
        params.append(last)

    if city:
        query += " AND UPPER(PROVIDER_CITY_NAME) = UPPER(%s)"
        params.append(city)

    if state:
        query += " AND UPPER(PROVIDER_STATE_NAME) = UPPER(%s)"
        params.append(state)

    query += " LIMIT 20;"

    conn = get_snowflake_connection()
    cur = conn.cursor()

    cur.execute(query, params)
    rows = cur.fetchall()
    columns = [c[0] for c in cur.description]

    cur.close()
    conn.close()

    return [dict(zip(columns, r)) for r in rows]
