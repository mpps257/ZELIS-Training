from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.cache import get_from_cache, save_to_cache
from app.search_snowflake import search_by_npi, search_by_filters
from app.nppes_fetcher import fetch_npi_by_number, fetch_npi_by_filters
from app.cleaner import clean_nppes_record
from app.db_insert import insert_into_snowflake

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search/npi/{npi}")
def search_npi(npi: str):

    cache_key = f"npi:{npi}"

    cached = get_from_cache(cache_key)
    if cached:
        return {"source": "cache", "data": cached}

    result = search_by_npi(npi)
    if not result:
        return {"message": "No provider found for this NPI"}

    save_to_cache(cache_key, result)

    return {"source": "snowflake", "data": result}



@app.get("/search/provider")
def search_provider(
    first_name: str = Query(None),
    last_name: str = Query(None),
    city: str = Query(None),
    state: str = Query(None)
):

    cache_key = f"search:{first_name}:{last_name}:{city}:{state}"

    cached = get_from_cache(cache_key)
    if cached:
        return {"source": "cache", "results": cached}

    results = search_by_filters(first_name, last_name, city, state)

    if not results:
        return {"message": "No providers found"}

    save_to_cache(cache_key, results)

    return {"source": "snowflake", "results": results}


@app.post("/inject/npi/{npi}")
def inject_npi(npi: str):

    raw = fetch_npi_by_number(npi)
    clean_row = clean_nppes_record(raw)

    if not clean_row:
        return {"message": "NPI not found in NPPES registry"}

    insert_into_snowflake(clean_row)

    save_to_cache(f"npi:{npi}", clean_row)

    return {
        "message": "NPI injected successfully",
        "source": "nppes",
        "data": clean_row
    }

@app.post("/inject/provider")
def inject_by_filters(
    first_name: str = Query(None),
    last_name: str = Query(None),
    city: str = Query(None),
    state: str = Query(None)
):

    raw = fetch_npi_by_filters(first_name, last_name, city, state)

    if raw.get("result_count", 0) == 0:
        return {"message": "No providers found in NPPES with these filters"}

    inserted_rows = []

    for r in raw.get("results", []):

        clean_row = clean_nppes_record({"result_count": 1, "results": [r]})

        insert_into_snowflake(clean_row)

        save_to_cache(f"npi:{clean_row['NPI']}", clean_row)

        inserted_rows.append(clean_row)

    return {
        "message": "Providers injected successfully",
        "count": len(inserted_rows),
        "data": inserted_rows
    }
