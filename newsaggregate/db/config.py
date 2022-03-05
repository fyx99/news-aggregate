import os

CONNECTION_DETAILS = {
    "dbname": os.environ.get("DB_NAME", default="news-aggregate"),
    "host": os.environ.get("DB_HOST", default="172.17.0.1"),
    "user": os.environ.get("DB_USER", default="postgres"),
    "password": os.environ.get("DB_PW", default="pwd"),
    "port": os.environ.get("DB_PORT", default="5432"),
    "application_name": "NEWSAGGREGATE"
}

TIMEOUT = os.environ.get("TIMEOUT", default=600)

HTTP_TIMEOUT = 7
