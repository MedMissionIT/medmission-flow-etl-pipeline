STAR_SCHEMA = {

    "dimensions": [
        "dim_patient",
        "dim_provider",
        "dim_date",
        "dim_site"
    ],

    "facts": [
        "fact_visit",
        "fact_diagnosis",
        "fact_prescription",
        "fact_ophtalmo_screening",
        "fact_ophtalmo_surgery"
    ]
}