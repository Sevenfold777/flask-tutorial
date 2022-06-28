import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app(test_config = None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True) # configuration files are relative to instance folder, will be allocated outside of flaskr
    app.config.from_mapping(
        SECRET_KEY='dev',   # to keep data safe
        DATABASE=os.path.join(app.instance_path, "flask.sqlite"), # path where database will be saved
    )
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    @app.route("/hello")
    def hello():
        return "Hello, World!"
    
    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    return app