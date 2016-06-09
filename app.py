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


@app.route('/')
def main():
    # refreshed_data = refresh()

    # Hardcoding data until we can store it in Redis
    refreshed_data = [('Ben', {'most_played_hero': u'junkrat', 'level': 58, 'handle': 'Trillium-1317',
                               'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x025000000000091D_Border.png',
                               'portrait': 'img/portrait/junkrat.png'}),
                      ('Chris', {'most_played_hero': u'junkrat', 'level': 41, 'handle': 'musa-1521',
                                 'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x025000000000091C_Border.png',
                                 'portrait': 'img/portrait/junkrat.png'}),
                      ('Lee', {'most_played_hero': u'genji', 'level': 33, 'handle': 'Taystamah-1107',
                               'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x025000000000091B_Border.png',
                               'portrait': 'img/portrait/genji.png'}),
                      ('Anna', {'most_played_hero': u'mercy', 'level': 50, 'handle': 'katana-12677',
                                'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x025000000000091C_Border.png',
                                'portrait': 'img/portrait/mercy.png'}),
                      ('Jack', {'most_played_hero': u'soldier-76', 'level': 23, 'handle': 'J4ck-1721',
                                'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x025000000000091A_Border.png',
                                'portrait': 'img/portrait/soldier-76.png'}),
                      ('Allen', {'most_played_hero': u'reinhardt', 'level': 17, 'handle': 'alhole-1287',
                                 'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x0250000000000919_Border.png',
                                 'portrait': 'img/portrait/reinhardt.png'}),
                      ('Kevin', {'most_played_hero': u'roadhog', 'level': 23, 'handle': 'Humula-1258',
                                 'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x025000000000091A_Border.png',
                                 'portrait': 'img/portrait/roadhog.png'}),
                      ('Maria', {'most_played_hero': u'dva', 'level': 36, 'handle': 'Coco-13179',
                                'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x025000000000091B_Border.png',
                                'portrait': 'img/portrait/dva.png'}),
                      ('Steve', {'most_played_hero': u'mei', 'level': 7, 'handle': 'Stevethomp-1228',
                                 'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x0250000000000918_Border.png',
                                 'portrait': 'img/portrait/mei.png'}),
                      ('Karen', {'most_played_hero': u'pharah', 'level': 2, 'handle': 'kamentari-1337',
                                'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x0250000000000918_Border.png',
                                'portrait': 'img/portrait/pharah.png'}),
                      ('Mitchel', {'most_played_hero': u'pharah', 'level': 1, 'handle': 'Remind-11496',
                                   'level_frame_img_url': u'https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/0x0250000000000918_Border.png',
                                   'portrait': 'img/portrait/pharah.png'})
                      ]

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
        player[1]['level'] = int(level)

        # Scrapes level and its frame image URL
        level_frame_scraping_index = response.text.find('playerlevelrewards')
        frame_img_url_pool = response.text[level_frame_scraping_index - 45: level_frame_scraping_index + 50]
        level_frame_img_url = frame_img_url_pool[frame_img_url_pool.find('http'):frame_img_url_pool.find('.png') + 4]
        player[1]['level_frame_img_url'] = level_frame_img_url
        # break
    return players

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
