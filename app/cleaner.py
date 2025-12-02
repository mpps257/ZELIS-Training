def clean_nppes_record(raw):

    if raw.get("result_count") == 0:
        return None

    r = raw["results"][0]

    basic = r.get("basic", {})
    taxonomies = r.get("taxonomies", [])
    addresses = r.get("addresses", [])

    specialty = taxonomies[0].get("desc") if len(taxonomies) > 0 else None

    loc = next((a for a in addresses if a.get("address_purpose") == "LOCATION"), {})

    return {
        "NPI": r.get("number"),
        "SPECIALITY": specialty,
        "PROVIDER_ORGANIZATION_NAME": basic.get("organization_name"),
        "PROVIDER_LASTNAME": basic.get("last_name"),
        "PROVIDER_FIRSTNAME": basic.get("first_name"),
        "PROVIDER_MIDDLENAME": basic.get("middle_name"),
        "EMPLOYER_IDENTIFICATION_NUMBER": basic.get("ein"),
        "PROVIDER_ADDRESS": loc.get("address_1"),
        "PROVIDER_CITY_NAME": loc.get("city"),
        "PROVIDER_STATE_NAME": loc.get("state"),
        "PROVIDER_POSTALCODE": loc.get("postal_code"),
    }
