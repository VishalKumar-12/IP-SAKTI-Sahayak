from flask import Flask, jsonify,render_template, request, send_from_directory
from flask_cors import CORS

from backend.routes.chat_routes import chat_bp
from backend.config import Config
from backend.extensions import db, jwt
from backend.routes.abs_routes import abs_bp
from backend.routes.source_routes import source_bp
from backend.routes.tkdl_routes import tkdl_bp
from backend.routes.classification_routes import classification_bp
from backend.routes.feedback_routes import feedback_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.history_routes import history_bp


app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})

# CORS(
#     app,
#     resources={
#         r"/api/*": {
#             "origins": [Config.FRONTEND_ORIGIN]
#         }
#     }
# )

db.init_app(app)
jwt.init_app(app)

with app.app_context():
    # Import models so SQLAlchemy is aware of them before create_all().
    from backend import models  # noqa: F401
    db.create_all()


app.register_blueprint(chat_bp, url_prefix="/api")
app.register_blueprint(abs_bp, url_prefix="/api")
app.register_blueprint(source_bp, url_prefix="/api")
app.register_blueprint(tkdl_bp, url_prefix="/api")
app.register_blueprint(classification_bp, url_prefix="/api")
app.register_blueprint(feedback_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(history_bp, url_prefix="/api")


@jwt.unauthorized_loader
def _unauthorized(reason):
    return jsonify({
        "success": False,
        "error": "Authentication required. Please log in."
    }), 401


@jwt.invalid_token_loader
def _invalid_token(reason):
    return jsonify({
        "success": False,
        "error": "Invalid or expired session. Please log in again."
    }), 401


@jwt.expired_token_loader
def _expired_token(jwt_header, jwt_payload):
    return jsonify({
        "success": False,
        "error": "Your session has expired. Please log in again."
    }), 401

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "service": "IP-SAKTI Sahayak",
        "message": "Backend is running"
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "IP-SAKTI Sahayak"
    })


@app.errorhandler(Exception)
def handle_error(error):
    print("Server Error:", error)

    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=Config.PORT,
        debug=False
    )