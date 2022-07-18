import os

POSTGRES_CONNECTION_DETAILS = {
    "dbname": os.environ.get("DB_NAME", default=""),
    "host": os.environ.get("DB_HOST", default=""),
    "user": os.environ.get("DB_USER", default=""),
    "password": os.environ.get("DB_PW", default=""),
    "port": os.environ.get("DB_PORT", default=""),
    "application_name": "NEWSAGGREGATE",
}

ASYNC_POSTGRES_CONNECTION_DETAILS = {
    "database": os.environ.get("DB_NAME", default=""),
    "host": os.environ.get("DB_HOST", default=""),
    "user": os.environ.get("DB_USER", default=""),
    "password": os.environ.get("DB_PW", default=""),
    "port": os.environ.get("DB_PORT", default="")
}

RABBIT_CONNECTION_DETAILS = {
    "host": os.environ.get("RB_HOST", default=""),
    "user": os.environ.get("RB_USER", default=""),
    "password": os.environ.get("RB_PW", default=""),
    "port": os.environ.get("RB_PORT", default=""),
}


NEWS_RECOMMEND = {
    "port": os.environ.get("NR_PORT", default="8000"),
}


TIMEOUT = os.environ.get("TIMEOUT", default=600)

HTTP_TIMEOUT = 4
