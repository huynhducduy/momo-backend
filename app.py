from flask import Flask
from flask_cors import CORS
from flask import jsonify, request, session, abort
from pypika import MySQLQuery as Query, Table, Field
import jwt

import config
from db import *

from model.merchant import Merchant
from model.category import Category
from model.store import Store
from model.transaction import Transaction
from model.user import User

import auth

app = Flask(__name__)
CORS(app)
app.secret_key = config.SECRET_KEY


@app.route("/v1/auth/login", methods=["POST"])
def login():
    if request.is_json:
        data = request.get_json(silent=True)
        if data == None:
            abort(400)
        else:
            phone = data.get("phone")
            password = data.get("password")

            cursor = get_db().cursor()

            user = Table("user")
            q = (
                Query.from_(user)
                .select(user.id)
                .where(user.phone == phone)
                .where(user.password == password)
            )

            cursor.execute(str(q))
            record = cursor.fetchone()
            cursor.close()

            if (record) != None:
                return jsonify({"token": auth.encode(record[0])})
            else:
                abort(404)
    else:
        abort(400)


@app.route("/v1/auth/me")
@auth.token_required
def user_info(user_id):

    user = Table("user")
    q = (
        Query.from_(user)
        .select(user.id, user.phone, user.name)
        .where(user.id == user_id)
    )

    cursor = get_db().cursor()
    cursor.execute(str(q))
    record = cursor.fetchone()
    cursor.close()

    return jsonify(User(record))


@app.route("/v1/auth/register")
def register():
    return True


@app.route("/v1/search")
@auth.token_required
def search(user_id):
    q = request.args.get("q")
    sort = request.args.get("sort")
    p = request.args.get("p")
    category = request.args.get("category")
    location = request.args.get("location")

    store = Table("store")
    q = Query.from_(store).select("*").limit(10)

    cursor = get_db().cursor()
    cursor.execute(str(q))
    records = cursor.fetchall()
    cursor.close()

    records = list(map(Store, records))
    return jsonify({"name": "Một cái tên nào đó", "stores": records})

    # if location is None:
    #     return abort(400)


@app.route("/v1/merchants", methods=["GET"])
def merchant():
    # request.args.get('title', '')
    # request.method

    # SELECT * FROM posts WHERE category=1 AND id < 12345 ORDER BY id DESC LIMIT 10

    cursor = db.get_connection().cursor()
    cursor.execute("SELECT * FROM merchant LIMIT 0,10")

    records = cursor.fetchall()
    records = list(map(Merchant, records))
    return jsonify(records)
    # response = app.response_class(
    #     response=json.dumps(data),
    #     mimetype='application/json'
    # )


@app.route("/v1/merchants/<int:id>", methods=["GET"])
def merchant1(id):
    res = {"error": "coac"}
    if request.is_json:
        data = request.get_json(silent=True)
        if data == None:
            return jsonify(**res), 400
    else:
        abort(400)
    return str(request.form["username"]) + "" + str(id)


@app.route("/v1/categories", methods=["GET"])
@auth.token_required
def categories(user_id):
    category = Table("category")
    q = Query.from_(category).select(category.id, category.name)

    cursor = get_db().cursor()
    cursor.execute(str(q))
    records = cursor.fetchall()
    cursor.close()

    records = list(map(Category, records))
    return jsonify(records)


# @app.route("/v1/categories/<int:id>", methods=["GET"])
# @auth.token_required
# def category(user_id, id):
#     merchant = Table("merchant")
#     q = Query.from_(merchant).select("*")

#     cursor = get_db().cursor()
#     cursor.execute(str(q))
#     records = cursor.fetchall()
#     cursor.close()

#     records = list(map(Merchant, records))
#     return jsonify(records)


# resp.set_cookie('username', 'the username')
# return redirect(url_for('login'))
# return render_template('page_not_found.html'), 404: (response, status), (response, headers), or (response, status, headers)
# resp = make_response(render_template('error.html'), 404)
# resp.headers['X-Something'] = 'A value'
# abort(401)
# request.cookies.get('username')
# url_for('profile', username='John Doe')
# url_for('static', filename='style.css')
# request.files['the_file']
# session['username'] = request.form['username']
# session.pop('username', None)
# escape()
# app.logger.debug('A value for debugging')
# app.logger.warning('A warning occurred (%d apples)', 42)
# app.logger.error('An error occurred')


if __name__ == "__main__":
    app.run(debug=True)
