import config

from flask import current_app, g

import mysql.connector as mysql
from pypika import MySQLQuery as Query, Table, Field


def get_db():
    if "db" not in g:
        g.db = mysql.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASS,
            database=config.MYSQL_DATABASE,
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


__all__ = ["close_db", "get_db"]

# cursor = db.cursor()
# cursor.execute(str(q))
# cursor.close()
# db.commit()
# db.close()
