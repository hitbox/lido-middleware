from .admin import admin_bp
from .crewmembers import crewmember_bp
from .user import user_bp
from .objects import objects_bp

def init_app(app):
    app.register_blueprint(crewmember_bp, url_prefix='/crewmembers')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(objects_bp, url_prefix='/objects')
