# from .base import db
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def init_app(app):
    # app.config.from_object('config')  
    
    db.init_app(app)
    
