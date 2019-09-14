import config
import mysql.connector as mysql
from pypika import MySQLQuery as Query, Table, Field

db = mysql.connect(
    host=config.MYSQL_HOST,
    port=config.MYSQL_PORT,
    user=config.MYSQL_USER,
    password=config.MYSQL_PASS,
    database=config.MYSQL_DATABASE,
)

# cursor = db.cursor()

# q = Query.into(Table('merchant'))

# cursor.execute(str(q))
# cursor.close()
# db.commit()


def close():
    db.close()
