from flask import render_template

from . import frontend_bp


@frontend_bp.route("/")
def home():
    return render_template("home.html", page_name="home")


@frontend_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", page_name="dashboard")
