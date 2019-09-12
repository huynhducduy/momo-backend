import config
import mysql.connector as mysql
from pypika import Query, Table, Field

db = mysql.connect(
    host=config.MYSQL_HOST,
    port=config.MYSQL_PORT,
    user=config.MYSQL_USER,
    password=config.MYSQL_PASS,
    database=config.MYSQL_DATABASE,
)

cursor = db.cursor()

q = Query.from_("customers").select("id", "fname", "lname", "phone")
cursor.execute(q)