import sqlite3

import  click
from flask import current_app, g
from flask.cli import with_appcontext

# g: special object that is unique for each request; 
# used to store data that might be accessed by muliple funcs;

# current_app: points to Flask application handling the request

def get_db():
    if ('db' not in g):
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()
        
        
def init_db():
    db = get_db()
    
    with current_app.open_resource('schema.sql') as f:  # open_resource: opens file relative to flaskr package
        db.executescript(f.read().decode("utf8"))
    
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initializede the database.")
    

def init_app(app):
    app.teardown_appcontext(close_db)   # tells Flask to call that func, when cleaning up after returning the response
    app.cli.add_command(init_db_command)    # add a new command that can be called with the "flask" command