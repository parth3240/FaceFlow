import psycopg2

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "facedetection"
DB_USER = "facedetect"
DB_PASS = "admin"


def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn
