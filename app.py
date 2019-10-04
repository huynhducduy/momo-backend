from flask import Flask
from flask_cors import CORS
from flask import jsonify, request, session, abort
from pypika import MySQLQuery as Query, Table, Field
from utils import fuzzy
import time
import jwt
from decimal import Decimal, DecimalException

import config
from db import *

from model.merchant import Merchant
from model.category import Category
from model.store import Store
from model.transaction import Transaction
from model.user import User
from model.suggestion import Suggestion

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
            fb_id = data.get("fb_id")
            phone = data.get("phone")
            password = data.get("password")

            cursor = get_db().cursor()

            user = Table("user")
            q = Query.from_(user).select(user.id)

            if fb_id != None:
                q = q.where(user.fb_id == fb_id)
            else:
                q = q.where(user.phone == phone).where(user.password == password)

            cursor.execute(str(q))
            record = cursor.fetchone()
            cursor.close()

            if (record) != None:
                return jsonify({"token": auth.encode(record[0])})
            else:
                abort(404)
    else:
        abort(400)


@app.route("/v1/auth/me", methods=["GET"])
@auth.token_required
def user_info(user_id):

    user = Table("user")
    q = (
        Query.from_(user)
        .select(user.id, user.name, user.phone, user.fb_id, user.created_on)
        .where(user.id == user_id)
    )

    cursor = get_db().cursor()
    cursor.execute(str(q))
    record = cursor.fetchone()
    cursor.close()

    transaction = Table("transaction")
    q = "SELECT COUNT(*) FROM transaction WHERE user_id = " + str(record[0])
    cursor = get_db().cursor()
    cursor.execute(str(q))
    trans = cursor.fetchone()
    cursor.close()

    record = record + (trans[0] == 0,)

    return jsonify(User(record))


@app.route("/v1/auth/register", methods=["POST"])
def register():
    if request.is_json:
        data = request.get_json(silent=True)
        if data == None:
            abort(400)
        else:
            fb_id = data.get("fb_id")
            phone = data.get("phone")
            password = data.get("password")
            name = data.get("name")

            if phone == None or password == None or name == None:
                abort(400)

            cursor = get_db().cursor()

            user = Table("user")
            q = Query.from_(user).select(user.id)

            if fb_id != None:
                q = q.where((user.phone == phone) | (user.fb_id == fb_id))
            else:
                q = q.where(user.phone == phone)
            q = q.limit(1)

            cursor.execute(str(q))
            record = cursor.fetchone()
            cursor.close()

            if record != None:
                return jsonify({"mesage": "user existed"}), 400
            else:
                q = Query.into(user)

                columns = ["phone", "password", "name", "created_on"]
                values = [phone, password, name, int(time.time() * 1000)]

                if fb_id:
                    columns.append("fb_id")
                    values.append(fb_id)

                cursor = get_db().cursor()
                q = q.columns(*columns).insert(*values)

                cursor.execute(str(q))
                record = cursor.fetchone()
                cursor.close()

                get_db().commit()

                return {"message": "success"}, 200
    else:
        abort(400)


@app.route("/v1/auth/connect", methods=["POST"])
@auth.token_required
def connect(user_id):
    if request.is_json:
        data = request.get_json(silent=True)
        if data == None:
            abort(400)
        else:
            fb_id = data.get("fb_id")

            if fb_id == None:
                abort(400)

            cursor = get_db().cursor()

            user = Table("user")
            q = Query.from_(user).select(user.id).where(user.fb_id == fb_id).limit(1)

            cursor.execute(str(q))
            record = cursor.fetchone()
            cursor.close()

            if record != None:
                return (
                    jsonify({"mesage": "facebok account connected to another user"}),
                    400,
                )
            else:
                q = Query.update(user).set(user.fb_id, fb_id).where(user.id == user_id)

                cursor = get_db().cursor()
                cursor.execute(str(q))
                cursor.close()

                get_db().commit()

                return {"message": "success"}, 200
    else:
        abort(400)


@app.route("/v1/auth/connect", methods=["DELETE"])
@auth.token_required
def disconnect(user_id):
    user = Table("user")
    q = Query.update(user).set(user.fb_id, None).where(user.id == user_id)

    cursor = get_db().cursor()
    cursor.execute(str(q))
    cursor.close()

    get_db().commit()

    return {"message": "success"}, 200


@app.route("/v1/auth/me", methods=["POST"])
@auth.token_required
def change_info(user_id):
    if request.is_json:
        data = request.get_json(silent=True)
        if data == None:
            abort(400)
        else:
            phone = data.get("phone")
            password = data.get("password")
            name = data.get("name")

            cursor = get_db().cursor()

            user = Table("user")

            q = Query.update(user)

            if phone:
                q = q.set(user.phone, phone)

            if password:
                q = q.set(user.password, password)

            if name:
                q = q.set(user.name, name)

            q = q.where(user.id == user_id)

            cursor = get_db().cursor()
            cursor.execute(str(q))
            cursor.close()

            get_db().commit()

            return {"message": "success"}, 200
    else:
        abort(400)


@app.route("/v1/search", methods=["GET"])
@auth.token_required
def search(user_id):
    result = {}

    q_arg = request.args.get("q")
    sort_arg = request.args.get("sort")
    p_arg = request.args.get("p")
    category_arg = request.args.get("category")
    location_arg = request.args.get("location")
    zone_arg = request.args.get("zone")
    area_arg = request.args.get("area")
    filter_arg = request.args.get("filter")

    category = Table("category")
    merchant = Table("merchant")
    store = Table("store")

    q = ""
    haveLocation = False

    if location_arg:
        locations = location_arg.split(",")
        try:
            locations[0] = Decimal(locations[0])
            locations[1] = Decimal(locations[1])
            q = (
                "SELECT *, (6371*acos(cos(radians("
                + str(locations[0])
                + "))*cos(radians(lat))*cos(radians(`long`)-radians("
                + str(locations[1])
                + "))+sin(radians("
                + str(locations[0])
                + "))*sin(radians(lat)))) AS distance"
            )
            haveLocation = True
        except (ValueError, DecimalException):
            abort(400)
    else:
        q = "SELECT *"

    q += " FROM store"

    if sort_arg:
        if str(sort_arg) == "popular":
            c = "SELECT store_id, COUNT(*) as count FROM transaction GROUP BY store_id"
            q += " LEFT JOIN (" + c + ") AS count ON count.store_id = id"
        elif str(sort_arg) == "match":
            pass

    wheres = []

    if category_arg:
        q2 = Query.from_(category).select("*").where(category.id == category_arg)
        cursor = get_db().cursor()
        cursor.execute(str(q2))
        record = cursor.fetchone()
        cursor.close()

        if record == None:
            abort(400)
        else:
            result["category"] = Category(record)
            q2 = (
                Query.from_(merchant)
                .select(merchant.id)
                .where(merchant.category_id == category_arg)
            )
            cursor = get_db().cursor()
            cursor.execute(str(q2))
            merchants = cursor.fetchall()
            cursor.close()

            wheres.append(
                "store.merchant_id IN (" + ",".join(str(i[0]) for i in merchants) + ")"
            )

    if q_arg:
        wheres.append("store.name LIKE '%" + q_arg + "%'")

    if zone_arg:
        wheres.append("store.zone = " + zone_arg)

    if area_arg:
        wheres.append("store.area_level_2 = '" + area_arg + "'")

    q += " WHERE " + wheres[0]

    for i in wheres[1:]:
        q += " AND " + i

    if filter_arg:
        filters = filter_arg.split(";")
        for i in filters:
            splits = i.split(",")
            if splits[0] == "distance":
                if haveLocation:
                    q += (
                        " HAVING distance BETWEEN "
                        + str(splits[1])
                        + " AND "
                        + str(splits[2])
                    )

    if sort_arg:
        if str(sort_arg) == "popular":
            q += " ORDER BY count.count DESC"
        elif str(sort_arg) == "distance":
            if haveLocation:
                q += " ORDER BY distance ASC"

    if p_arg:
        try:
            p_arg = int(p_arg)
            q += " LIMIT " + str((p_arg - 1) * 10) + ", 10"
        except ValueError:
            return abort(400)

    cursor = get_db().cursor()
    cursor.execute(str(q))
    records = cursor.fetchall()
    cursor.close()

    newStore = lambda a: Store(a, 0)
    if not category_arg:
        newStore = lambda a: Store(a, 0)

    q = "INSERT INTO keyword(content, category, area, user_id, time, records"

    if zone_arg:
        q += ", zone"

    q += (
        ") VALUES('"
        + q_arg
        + "', '"
        + category_arg
        + "', '"
        + area_arg
        + "','"
        + str(user_id[0])
        + "',"
        + str(int(time.time() * 1000))
        + ","
        + str(len(records))
    )

    if zone_arg:
        q += "," + zone_arg

    q += ")"

    cursor = get_db().cursor()
    cursor.execute(q)
    cursor.close()
    get_db().commit()

    records = list(map(newStore, records))
    result["stores"] = records
    return jsonify(**result)


@app.route("/v1/suggest", methods=["GET"])
@auth.token_required
def suggest(user_id):

    q_arg = request.args.get("q")
    category_arg = request.args.get("category")

    if not q_arg:
        return jsonify({"suggestions": []})
    else:

        fuzz = fuzzy(q_arg)

        q = (
            "SELECT s.name, g.category_id, g.name FROM store AS s JOIN\
            (SELECT category.name, category_id, merchant_id, COUNT(*) AS count FROM transaction\
            JOIN store ON store.id = store_id\
            JOIN merchant ON store.merchant_id = merchant.id\
            JOIN category ON merchant.category_id = category.id\
            GROUP BY merchant_id) AS g ON (s.name LIKE '%"
            + str(q_arg)
            + "%' OR MATCH (s.name) AGAINST ('"
            + str(q_arg)
            + "' IN NATURAL LANGUAGE MODE)"
        )

        # for i in fuzz:
        #     q += " OR s.name LIKE '%" + str(i) + "%'"

        q += ") AND s.merchant_id = g.merchant_id"

        if category_arg:
            q += " AND g.category_id = " + str(category_arg)

        q += " ORDER BY g.count DESC LIMIT 0,10"

        cursor = get_db().cursor()
        cursor.execute(str(q))
        records = cursor.fetchall()
        cursor.close()

        records = list(map(Suggestion, records))
        return jsonify({"suggestions": records})


@app.route("/v1/zones", methods=["GET"])
@auth.token_required
def zones(user_id):

    result = {}

    store = Table("store")
    q = "SELECT DISTINCT area_level_2, area_level_1, zone FROM store WHERE zone != 0 ORDER BY area_level_2"

    cursor = get_db().cursor()
    cursor.execute(str(q))
    records = cursor.fetchall()
    cursor.close()

    if len(records) > 0:
        for r in records:
            if result.get(r[2]) == None:
                result[r[2]] = []
            result[r[2]].append(r[0])

    return jsonify(result)


@app.route("/v1/categories", methods=["GET"])
@auth.token_required
def categories(user_id):
    category = Table("category")
    q = Query.from_(category).select(category.id, category.name).orderby("order")

    cursor = get_db().cursor()
    cursor.execute(str(q))
    records = cursor.fetchall()
    cursor.close()

    records = list(map(Category, records))
    return jsonify(records)


@app.route("/v1/not-interested/<int:id>", methods=["POST"])
@auth.token_required
def not_interested(user_id, id):
    return jsonify({"message": "success"})


@app.route("/v1/not-interested/<int:id>", methods=["DELETE"])
@auth.token_required
def interested(user_id, id):
    return jsonify({"message": "success"})


@app.route("/v1/not-interested", methods=["GET"])
@auth.token_required
def list_interested(user_id):
    return jsonify({})

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
