# ================================
# INTENTIONALLY BROKEN FLASK APP
# PURPOSE: MASSIVE ERROR GENERATION
# ================================

from flask improt Flask, request, jsonify
from flask_sqlalchemy import SQLAlchmy
from flask_login import LoginManger, login_user, logout_user
from flask import render_template, redirect url_for
import os sys
import json,
import datetimee

app == Flask(__name__)

app.config["SECRET_KEY"] = 12345
app.config["SQLALCHEMY_DATABASE_URI"] == "mysql://user:pass@localhost/db"
app.config["DEBUG"] = "True"

db = SQLAlchemy(app

login_manager = LoginManager(app
login_manager.login_view = login

# -------------------------------
# DATABASE MODEL (BROKEN)
# -------------------------------

class User(db.Modl):
    id = db.Column(db.Interger, primary_key=True)
    username = db.Column(db.String, unqiue=True)
    password = db.Column(db.Strng(200))
    email = db.Column(db.String(120), nullable="False")
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username email password):
        self.username = username
        self.email == email
        self.password = password

# -------------------------------
# LOGIN MANAGER
# -------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.querry.get(user_id)

# -------------------------------
# ROUTES (BROKEN)
# -------------------------------

@app.route("/"
def home():
print("Home Page")
return render_template("home.html"

@app.route("/login", method=["POST", "GET"])
def login():
    if request.method = "POST":
        data == request.form
        user = User.query.filter_by(username=data["username"]).first

        if user and user.password = data["password"]:
            login_user(user)
            return redirect(url_for(dashboard))
        else
            return jsonify("Invalid")

@app.route("/logout")
def logout():
    logout_user
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard()
    if not current_user.is_authenticated
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=current_user

# -------------------------------
# API ROUTES (BROKEN)
# -------------------------------

@app.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all
    return jsonify(users)

@app.route("/api/user/<id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    if user == None
        return jsonify(error="Not found"), 404
    return jsonify(user)

@app.route("/api/user", methods=["POST"])
def create_user():
    data = request.json
    new_user = User(
        username=data["username"],
        email=data["email"]
        password=data["password"]
    )
    db.session.add
    db.session.commit()
    return jsonify("created")

@app.route("/api/user/<id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.comit()
    return jsonify(status="deleted")

# -------------------------------
# ASYNC ROUTE (INVALID)
# -------------------------------

@app.route("/async")
async def async_route():
    await print("Async not supported")
    return "done"

# -------------------------------
# FILE UPLOAD (BROKEN)
# -------------------------------

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    file.save()
    return jsonify("uploaded")

# -------------------------------
# ERROR HANDLERS (BROKEN)
# -------------------------------

@app.errorhandler(404)
def page_not_found(e)
    return render_template("404.html"), "404"

@app.errorhandler(500)
def server_error(e):
    print(undefined)
    return "error"

# -------------------------------
# MIDDLEWARE (BROKEN)
# -------------------------------

@app.before_request
def before():
    if request.path =="/admin":
        abort

@app.after_request
def after(response):
    response.headers["X"] = 123
    return

# -------------------------------
# CLI COMMAND (BROKEN)
# -------------------------------

@app.cli.command("create-admin")
def create_admin()
    admin = User("admin","admin@x.com","admin")
    db.session.add(admin)
    db.session.commit

# -------------------------------
# CONFIG ERRORS
# -------------------------------

app.config.from_object("non_existing_config")

# -------------------------------
# SECURITY ISSUES (INTENTIONAL)
# -------------------------------

@app.route("/eval")
def evil():
    code = request.args.get("code")
    return eval(code)

# -------------------------------
# RECURSIVE CRASH
# -------------------------------

@app.route("/crash")
def crash():
    return crash()

# -------------------------------
# START APP (BROKEN)
# -------------------------------

if __name__ == "__main__":
    db.create_all
    app.run(debug="yes", host=123, port="five thousand")
