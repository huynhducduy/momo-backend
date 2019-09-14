from flask import Flask
from flask_cors import CORS
from flask import jsonify, request, session, abort

import config
import db

from model.merchant import Merchant

app = Flask(__name__)
CORS(app)
app.secret_key = config.SECRET_KEY


@app.route("/v1/merchants", methods=["GET"])
def merchant():
    # request.args.get('title', '')
    # request.method

    # SELECT * FROM posts WHERE category=1 AND id < 12345 ORDER BY id DESC LIMIT 10

    cursor = db.db.cursor()
    cursor.execute("SELECT * FROM merchant LIMIT 0,10")

    records = cursor.fetchall()
    records = list(map(Merchant, records))
    return jsonify(records)
    # response = app.response_class(
    #     response=json.dumps(data),
    #     mimetype='application/json'
    # )


@app.route("/v1/merchant/<int:id>")
def merchant1(id):
    return str(request.form["username"]) + "" + str(id)


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
