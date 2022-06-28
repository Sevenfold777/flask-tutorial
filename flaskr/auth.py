from crypt import methods
import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth") # create blueprint; __name__ : to tell where it is defined

@bp.route("/register", methods=("Get", "POST"))
def register():
    if (request.method == "POST"):
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
            
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)
        
        
        
    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone() # sqlite
    
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
        
        
        if error is None:
            session.clear()
            session["user_id"] = user["id"] # Flask securely signs the data so that it can’t be tampered with.; - from official docs
            return redirect(url_for("index"))
        
        
        flash(error)
        
    return render_template("auth/login.html")

@bp.before_app_request  # registers a function that runs before the view function, no matter what url is requested
def load_logged_in_user():
    user_id = session.get("user_id")
    
    if (user_id is None):
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        
    # store user data in "g" so that it lasts for the length of the request
    
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))    


'''
    This decorator returns a new view function that wraps the original view it’s applied to. 
    user loaded - original view is called
    not loaded - redirect to login
'''
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if (g.user is None):
            return redirect(url_for("auth.login"))
        
        return view(**kwargs)
    
    return wrapped_view