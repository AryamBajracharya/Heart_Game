from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets

app = Flask(__name__)
CORS(app)

# In-memory user database
users = {}  # {username: {"password": "abc", "highscore": 0, "token": "xyz"}}

# -------------------- REGISTER -------------------- #
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    if username in users:
        return jsonify({"error": "Username already exists"}), 400

    users[username] = {"password": password, "highscore": 0, "token": ""}
    return jsonify({"message": "Registration successful!"}), 200

# -------------------- LOGIN -------------------- #
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username not in users or users[username]["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    token = secrets.token_hex(8)
    users[username]["token"] = token
    return jsonify({
        "message": "Login successful",
        "username": username,
        "token": token,
        "highscore": users[username]["highscore"]
    })

# -------------------- SUBMIT SCORE -------------------- #
@app.route("/submit_score", methods=["POST"])
def submit_score():
    data = request.get_json()
    token = data.get("token")
    score = data.get("score")

    if not token or score is None:
        return jsonify({"error": "Missing token or score"}), 400

    user = next((u for u, info in users.items() if info["token"] == token), None)
    if not user:
        return jsonify({"error": "Invalid token"}), 401

    if score > users[user]["highscore"]:
        users[user]["highscore"] = score

    return jsonify({"message": "Score updated", "highscore": users[user]["highscore"]}), 200

# -------------------- LEADERBOARD -------------------- #
@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    print("--- LEADERBOARD REQUEST ---")
    print("Current users:", users)
    leaderboard_data = [
        {"username": u, "highscore": info["highscore"]}
        for u, info in users.items()
    ]
    leaderboard_data.sort(key=lambda x: x["highscore"], reverse=True)
    print("Leaderboard data being sent:", leaderboard_data)
    print("--------------------------")
    return jsonify({"leaderboard": leaderboard_data}), 200

# -------------------- HIGHSCORE -------------------- #
@app.route("/highscore/<username>", methods=["GET"])
def get_highscore(username):
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"highscore": users[username]["highscore"]}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
