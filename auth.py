from flask import current_app
import jwt
import datetime
from flask import jsonify, request
from pypika import MySQLQuery as Query, Table, Field
from db import *
from functools import wraps


def encode(user_id):
    try:
        payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "sub": user_id,
        }
        return jwt.encode(payload, current_app.secret_key, algorithm="HS256").decode(
            "utf-8"
        )
    except Exception as e:
        return e


def decode(token):
    return jwt.decode(token, current_app.secret_key, algorithms=["HS256"])


def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get("Authorization", "").split()

        invalid_msg = {"message": "invalid token"}

        expired_msg = {"message": "expired token"}

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = decode(token) 

            user = Table("user")
            q = Query.from_(user).select(user.id).where(user.id == data["sub"])

            cursor = get_db().cursor()
            cursor.execute(str(q))
            record = cursor.fetchone()
            cursor.close()

            if not record:
                raise RuntimeError("User not found")
            return f(record, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401  # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError) as e:
            print(e)
            return jsonify(invalid_msg), 401

    return _verify
