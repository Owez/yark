"""Flask extensions which are used at import-time before being integrated into the final app"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
