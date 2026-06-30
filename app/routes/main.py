from flask import Blueprint, jsonify, render_template
from flask_login import login_required


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main_bp.get("/healthz")
def healthz():
    return jsonify(status="ok")
