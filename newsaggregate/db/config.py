import os

POSTGRES_CONNECTION_DETAILS = {
    "dbname": os.environ.get("DB_NAME", default="newsaggregate"),
    "host": os.environ.get("DB_HOST", default="138.68.74.3"),
    "user": os.environ.get("DB_USER", default="postgres"),
    "password": os.environ.get("DB_PW", default="u3fph3ßü98fg43f34f3"),
    "port": os.environ.get("DB_PORT", default="5432"),
    "application_name": "NEWSAGGREGATE",

}

RABBIT_CONNECTION_DETAILS = {
    "host": os.environ.get("RB_HOST", default="138.68.74.3"),
    "user": os.environ.get("RB_USER", default="dog"),
    "password": os.environ.get("RB_PW", default="20849hfibfcn82..SADFC"),
    "port": os.environ.get("RB_PORT", default="5672"),
}




TIMEOUT = os.environ.get("TIMEOUT", default=600)

HTTP_TIMEOUT = 4
