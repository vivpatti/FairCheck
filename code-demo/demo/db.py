import sqlite3
import click
from flask import current_app, g

def get_db():
    #The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.
    if 'db' not in g:
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
    with current_app.open_resource('./demo/faircheck-demo.sql') as f:
        db.executescript(f.read().decode('utf8'))
    print('Initialized the database.')

