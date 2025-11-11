from flask import Flask, g, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = '~/theboard.db'

def get_db():
    try:
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # Makes queries return rows (namedtuples) so they can be accessed by index or key
        return db
    except sqlite3.OperationalError as e:
        print(e)

def query_db(query, args=(), one=False):
    try:
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return(rv[0] if rv else None) if one else rv
    except sqlite3.OperationalError as e:
        print(e)

@app.route("/message", methods=['GET', 'POST'])
def handle_post():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' field in POST request"}), 400
    # Check if message is valid
    message = data.message
    if not message or not isinstance(message, str) or len(message) > 25:
        return jsonify({"error": "Invalid message was entered"})
    # Get db, upsert message, return 200
    query_db('UPDATE message SET message=? WHERE id = 1;', data.message)
    return jsonify({"message": "Message has successfully been updated to database"}), 200

def handle_get():
    message = query_db('SELECT message FROM message WHERE id=1;',None, True)
    if not message:
        return jsonify({"error": "Missing message in database, unable to GET"})
    return jsonify({"message": message}), 200

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()