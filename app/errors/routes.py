from flask import render_template
from . import errors_bp


@errors_bp.errorhandler(404)
def error_404(e):
    return render_template("errors/404.html", error="404"), 404


@errors_bp.errorhandler(500)
def error_500(e):
    return render_template("errors/500.html", error="500"), 500