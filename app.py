# -*- coding: utf-8 -*-
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('OVERWATCHSTATS_SETTINGS', silent=True)


@app.before_request
def before_request():
    pass

@app.route('/')
def main():
    return render_template('index.html')

"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            username = ?''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)
"""

# add some filters to jinja
#app.jinja_env.filters['datetimeformat'] = format_datetime
#app.jinja_env.filters['gravatar'] = gravatar_url

if __name__== "__main__":
    app.run()
