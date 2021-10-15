from .dashboard import dashboard
from dash import Dash
# from projectApp.models import state

def init_app(app):
    with app.app_context():
        from projectApp.models.state import state
    app.register_blueprint(dashboard, url_prefix='')

    # from .models import state

