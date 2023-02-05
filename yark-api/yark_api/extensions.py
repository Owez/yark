"""Flask extensions which are used at import-time before being integrated into the final app"""

from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_caching import Cache
from flask_cors import CORS

db = SQLAlchemy()
api = Api()
cache = Cache()
cors = CORS()
