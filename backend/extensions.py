"""
Shared Flask extension instances.

Kept in their own module (instead of inside app.py) so that models.py,
routes, etc. can import `db` / `jwt` without causing circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()
