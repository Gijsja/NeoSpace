from flask import Blueprint, send_from_directory, g, redirect, url_for, render_template

bp = Blueprint('views', __name__)

@bp.route("/")
def index():
    if g.user is None:
         return redirect(url_for("auth.login"))
    return render_template("app.html")

@bp.route("/app")
def app_view():
    if g.user is None:
         return redirect(url_for("auth.login"))
    return render_template("app.html")

@bp.route("/dashboard")
def dashboard():
    if g.user is None:
         return redirect(url_for("auth.login"))
    return render_template("dashboard.html")

@bp.route("/directory")
def directory():
    if g.user is None:
         return redirect(url_for("auth.login"))
    return render_template("directory.html")

@bp.route("/codeground")
def codeground():
    if g.user is None:
         return redirect(url_for("auth.login"))
    return render_template("codeground.html")

@bp.route("/components")
def components():
    if g.user is None:
         return redirect(url_for("auth.login"))
    return render_template("playground.html")

@bp.route("/penguin")
def penguin():
    if g.user is None:
         return redirect(url_for("auth.login"))
    return render_template("penguin_test.html")

@bp.route("/desktop")
def desktop():
    if g.user is None:
         return redirect(url_for("auth.login"))
    return send_from_directory("ui/views", "desktop.html")

@bp.route("/ui/css/<path:filename>")
def serve_css(filename):
    return send_from_directory("ui/css", filename)

@bp.route("/ui/js/<path:filename>")
def serve_js(filename):
    return send_from_directory("ui/js", filename)

@bp.route("/ui/views/<path:filename>")
def serve_views(filename):
    return send_from_directory("ui/views", filename)

@bp.route("/static/uploads/<path:filename>")
def serve_uploads(filename):
    return send_from_directory("static/uploads", filename)

@bp.route("/static/avatars/<path:filename>")
def serve_avatars(filename):
    return send_from_directory("static/avatars", filename)

@bp.route("/static/voice_intros/<path:filename>")
def serve_voice_intros(filename):
    return send_from_directory("static/voice_intros", filename)

@bp.route("/ui/prototypes/<path:filename>")
def serve_prototypes(filename):
    return send_from_directory("ui/prototypes", filename)
