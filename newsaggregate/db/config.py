import os

CONNECTION_DETAILS = {
    "dbname": os.environ.get("DB_NAME", default="newsaggregate"),
    "host": os.environ.get("DB_HOST", default="138.68.74.3"),
    "user": os.environ.get("DB_USER", default="postgres"),
    "password": os.environ.get("DB_PW", default="u3fph3ßü98fg43f34f3"),
    "port": os.environ.get("DB_PORT", default="5432"),
    "application_name": "NEWSAGGREGATE"
}

TIMEOUT = os.environ.get("TIMEOUT", default=600)

HTTP_TIMEOUT = 4
