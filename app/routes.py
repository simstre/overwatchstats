import requests, json
from redis import Redis
from datetime import datetime
from pytz import timezone
from flask import session, url_for, redirect, render_template

from app.base import app
from app.constants import REDIS_URL, OVERWATCH_URL, PLAYERS, MASTEROVERWATCH_URL, OVERWATCHTRACKER_URL
from app.scraper import _scrape_competitive_data, _scrape_quickplay_data


redis_store = Redis(host=REDIS_URL)

@app.route('/')
def main():
    """
    Dashboard

    :return:
    """
    data = []
    for player in PLAYERS:
        try:
            player_dict = json.loads(redis_store.hget('players_list', player[0]))
            data.append((player[0], player_dict))
        except:
            continue

    last_updated = redis_store.get('last_updated')
    data_sorted_by_level = sorted(data, key=lambda player: player[1]['games_won'], reverse=True)
    return render_template('index.html', overwatch_url=OVERWATCH_URL, players=data_sorted_by_level, last_updated=last_updated, masterow_url=MASTEROVERWATCH_URL, owtracker_url=OVERWATCHTRACKER_URL)


@app.route('/refresh_data')
def refresh():
    """
    This scrapes the data and stores the data in Redis for display

    :return:
    """
    for player in PLAYERS:
        try:
            response = requests.get(OVERWATCH_URL.format(player[1]['handle']))

            player = _scrape_quickplay_data(response, player)
            if response.text.find('competitive-rank') > 0:
                player = _scrape_competitive_data(response, player)

            # Stores into Redis
            redis_store.hset('players_list', player[0], json.dumps(player[1]))
        except Exception as e:
            # log exception and move on
            pass
    redis_store.set('last_updated', datetime.now(timezone('US/Pacific')).strftime("%B %d %I:%M%p"))
    return 'Refresh successful'


@app.route('/scrape_and_store')
def scrape_and_store():
    """
    This scrapes the data and stores as a file for future tracking purpose

    :return:
    """
    for player in PLAYERS:
        today_timestamp = datetime.now().strftime("%Y%m%d")

        # Making a hit to popular OW stat sites so that they have daily data for all airG players
        response = requests.get(OVERWATCH_URL.format(player[1]['handle']))
        response = requests.get(OVERWATCH_URL.format(player[1]['handle']))

        response = requests.get(OVERWATCH_URL.format(player[1]['handle']))
        with open('/airg/logs/overwatchstats/scraped_data/{}_{}'.format(player[0], today_timestamp), 'w') as _f_handle:
            _f_handle.write(response.text.encode('ascii', 'ignore'))
    return 'Storing successful'


@app.route('/ping_stat_sites')
def ping_sites():
    """
    Pings popular OW stats tracking sites once a day to make them track our daily stats

    :return:
    """
    for player in PLAYERS:
        # Making a hit to popular OW stat sites so that they have daily data for all airG players
        try:
            response = requests.get(MASTEROVERWATCH_URL.format(player[1]['handle']))
            response = requests.get(OVERWATCHTRACKER_URL.format(player[1]['handle']))
        except:
            continue
    return 'poking complete'