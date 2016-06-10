import requests, json
from redis import Redis
import time
from flask import Flask, session, url_for, redirect, render_template


REDIS_URL = "chriss-fun-1.office.airg.lan"
overwatch_url = 'https://playoverwatch.com/en-us/career/pc/us/{}'

app = Flask(__name__)
redis_store = Redis(host=REDIS_URL)
app.config.from_object(__name__)

players = [
    ('Ben', {'handle': 'Trillium-1317'}),
    ('Chris', {'handle': 'musa-1521'}),
    ('Lee', {'handle': 'Taystamah-1107'}),
    ('Anna', {'handle': 'katana-12677'}),
    ('Jack', {'handle': 'J4ck-1721'}),
    ('Allen', {'handle': 'alhole-1287'}),
    ('Kevin', {'handle': 'Humula-1258'}),
    ('Maria', {'handle': 'Coco-13179'}),
    ('Steven', {'handle': 'Stevethomp-1228'}),
    ('TY', {'handle': 'TheOnlyTY-1643'}),
    ('Karen', {'handle': 'kamentari-1337'}),
    ('Mitchel', {'handle': 'Remind-11496'})
]


@app.route('/')
def main():
    """
    Dashboard

    :return:
    """
    data = []
    for player in players:
        player_dict = json.loads(redis_store.hget('players_list', player[0]))
        data.append((player[0], player_dict))
    return render_template('index.html', overwatch_url=overwatch_url, players=data)


@app.route('/refresh_data')
def refresh():
    """
    This scrapes the data and stores the data in Redis for display

    :return:
    """
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
        redis_store.hset('players_list', player[0], json.dumps(player[1]))
    return 'Refresh successful'


@app.route('/scrape_and_store')
def scrape_and_store():
    """
    This scrapes the data and stores as a file for future tracking purpose

    :return:
    """
    for player in players:
        today_timestamp = time.strftime("%Y%m%d")
        response = requests.get(overwatch_url.format(player[1]['handle']))
        with open('/airg/logs/overwatchstats/scraped_data/{}_{}'.format(player[0], today_timestamp)) as _f_handle:
            _f_handle.write(response.text)
    return 'Storing successful'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
