import requests

NPI_API_URL = "https://npiregistry.cms.hhs.gov/api/"

def _make_request(params: dict):
    try:
        response = requests.get(
            NPI_API_URL,
            params=params,
            timeout=8
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        return {"error": "NPPES API timeout"}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def fetch_npi_by_number(npi: str):
    params = {
        "number": npi,
        "version": "2.1"
    }

    return _make_request(params)

def fetch_npi_by_filters(first=None, last=None, city=None, state=None):
    params = {"version": "2.1"}

    if first:
        params["first_name"] = first
    if last:
        params["last_name"] = last
    if city:
        params["city"] = city
    if state:
        params["state"] = state

    return _make_request(params)
