import os
from flask import Blueprint, render_template, send_from_directory, current_app, Response

web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def index():
    return render_template("index.html")

@web_bp.route("/doctor")
def doctor():
    return render_template("doctor.html")

@web_bp.route("/clinic")
def clinic():
    return render_template("clinic.html")

@web_bp.route("/report")
def report():
    return render_template("report.html")

@web_bp.route("/visit-prep")
def visit_prep():
    return render_template("visit_prep.html")

@web_bp.route("/offline")
def offline():
    return render_template("offline.html")

@web_bp.route("/manifest.json")
def manifest():
    return send_from_directory(
        os.path.join(current_app.root_path, "..", "static"),
        "manifest.json",
        mimetype="application/manifest+json"
    )

@web_bp.route("/sw.js")
def service_worker():
    response = send_from_directory(
        os.path.join(current_app.root_path, "..", "static"),
        "sw.js",
        mimetype="application/javascript"
    )
    # Enable service worker control across the entire origin root
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response
