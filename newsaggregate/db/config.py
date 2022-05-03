import os

POSTGRES_CONNECTION_DETAILS = {
    "dbname": os.environ.get("DB_NAME", default=""),
    "host": os.environ.get("DB_HOST", default=""),
    "user": os.environ.get("DB_USER", default=""),
    "password": os.environ.get("DB_PW", default=""),
    "port": os.environ.get("DB_PORT", default=""),
    "application_name": "NEWSAGGREGATE",

}

RABBIT_CONNECTION_DETAILS = {
    "host": os.environ.get("RB_HOST", default=""),
    "user": os.environ.get("RB_USER", default=""),
    "password": os.environ.get("RB_PW", default=""),
    "port": os.environ.get("RB_PORT", default=""),
}




TIMEOUT = os.environ.get("TIMEOUT", default=600)

HTTP_TIMEOUT = 4
