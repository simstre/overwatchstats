# -*- coding: utf-8 -*-
from datetime import datetime
import requests
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('OVERWATCHSTATS_SETTINGS', silent=True)

overwatch_url = 'https://playoverwatch.com/en-us/career/pc/us/{}'
players = [
    ('Ben', {'handle': 'Trillium-1317'}),
    ('Chris', {'handle': 'musa-1521'}),
    ('Lee', {'handle': 'Taystamah-1107'}),
    ('Anna', {'handle': 'katana-12677'}),
    ('Jack', {'handle': 'J4ck-1721'}),
    ('Allen', {'handle': 'alhole-1287'}),
    ('Kevin', {'handle': 'Humula-1258'}),
    ('Maria', {'handle': 'Coco-13179'}),
    ('Steve', {'handle': 'Stevethomp-1228'}),
    ('Karen', {'handle': 'kamentari-1337'}),
    ('Mitchel', {'handle': 'Remind-11496'})
]

@app.before_request
def before_request():
    pass

@app.route('/')
def main():
    refreshed_data = refresh()
    return render_template('index.html', overwatch_url=overwatch_url, players=refreshed_data)

@app.route('/refresh_data')
def refresh():
    for player in players:
        response = requests.get(overwatch_url.format(player[1]['handle']))

        # Scrapes Most played hero
        portrait_img_starting_index = response.text.find('cloudfront.net/hero/')
        portrait_img_ending_index = response.text.find('/overlay-portrait.png')
        portrait_hero = response.text[portrait_img_starting_index + 20: portrait_img_ending_index]
        player[1]['most_played_hero'] = portrait_hero
        player[1]['portrait'] = 'img/portrait/{}.png'.format(portrait_hero)

        # Scrapes level
        level_index = response.text.find('<div class="u-vertical-center"')
        level_string_pool = response.text[level_index + 31: level_index + 34]
        level_ending_index = level_string_pool.find('<')
        level = level_string_pool[:level_ending_index]
        player[1]['level'] = level

        # Scrapes level and its frame image URL
        level_frame_scraping_index = response.text.find('playerlevelrewards')
        frame_img_url_pool = response.text[level_frame_scraping_index - 45: level_frame_scraping_index + 50]
        level_frame_img_url = frame_img_url_pool[frame_img_url_pool.find('http'):frame_img_url_pool.find('.png') + 4]
        player[1]['level_frame_img_url'] = level_frame_img_url
        #break
    return players

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
