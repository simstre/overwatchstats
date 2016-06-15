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
    ('Anna', {'handle': 'katana-12677'}),
    ('Chris', {'handle': 'musa-1521'}),
    ('Maria', {'handle': 'Coco-13179'}),
    ('Lee', {'handle': 'Taystamah-1107'}),
    ('Jack', {'handle': 'J4ck-1721'}),
    ('Kevin', {'handle': 'Humula-1258'}),
    ('Allen', {'handle': 'alhole-1287'}),
    ('TY', {'handle': 'TheOnlyTY-1643'}),
    ('Steven', {'handle': 'Stevethomp-1228'}),
    ('Perry', {'handle': 'quintonFOX-1789'}),
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
        most_played_hero = response.text[response.text.find('cloudfront.net/hero/'):].split('/')[2]
        player[1]['most_played_hero'] = most_played_hero
        player[1]['portrait'] = 'img/portrait/{}.png'.format(most_played_hero)

        # Scrapes level
        player[1]['level'] = int(response.text[response.text.find('<div class="u-vertical-center'):].split('>')[1][:-5])

        # Scrapes level frame image URL
        player[1]['level_frame_img_url'] = response.text[response.text.find('playerlevelrewards') - 45:].split('(')[1].split(')')[0]

        #############################################################################################################
        ##### Below scraping won't work if the player is new, all the calculation based on scraping goes below ######

        # Scrapes and calculates winrate
        if response.text.find('Games Won', 70000) == -1:
            continue
        games_won = response.text[response.text.find('Games Won', 70000):].split("</td>")[1][4:].replace(',', '')
        games_played = response.text[response.text.find('Games Played', 70000):].split("</td>")[1][4:].replace(',', '')
        player[1]['winrate'] = '{:.1f}'.format(float(games_won)/float(games_played) * 100)

        # Scrapes and calculates KDA
        defensive_assists = 0
        if response.text.find('<td>Defensive Assists</td>') != -1:
            defensive_assists = response.text[response.text.find('<td>Defensive Assists</td>'):].split('</td>')[1][4:].replace(',', '')
        offensive_assists = 0
        if response.text.find('<td>Defensive Assists</td>') != -1:
            offensive_assists = response.text[response.text.find('<td>Offensive Assists</td>'):].split('</td>')[1][4:].replace(',', '')

        kills = response.text[response.text.find('<td>Eliminations</td>'):].split('</td>')[1][4:].replace(',', '')
        deaths = response.text[response.text.find('<td>Deaths</td>'):].split('</td>')[1][4:].replace(',', '')
        player[1]['kda'] = '{:.2f}'.format((float(defensive_assists) + float(offensive_assists) + float(kills)) / float(deaths))

        # Stores into Redis
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
        with open('/airg/logs/overwatchstats/scraped_data/{}_{}'.format(player[0], today_timestamp), 'w') as _f_handle:
            _f_handle.write(response.text.encode('ascii', 'ignore'))
    return 'Storing successful'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
