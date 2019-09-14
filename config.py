import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DATABASE = (
    os.getenv("MYSQL_HOST"),
    int(os.getenv("MYSQL_PORT")),
    os.getenv("MYSQL_USER"),
    os.getenv("MYSQL_PASS"),
    os.getenv("MYSQL_DATABASE"),
)

ITEMS_PER_PAGE_DEFAULT = os.getenv("ITEMS_PER_PAGE_DEFAULT")
SECRET_KEY = os.getenv("SECRET_KEY")
