import requests, json
from redis import Redis
from datetime import datetime
from pytz import timezone
from flask import session, url_for, redirect, render_template

from app.base import app
from app.constants import REDIS_URL, OVERWATCH_URL, PLAYERS, MASTEROVERWATCH_URL, OVERWATCHTRACKER_URL


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
    return render_template('index.html', overwatch_url=OVERWATCH_URL, players=data_sorted_by_level, last_updated=last_updated)


@app.route('/refresh_data')
def refresh():
    """
    This scrapes the data and stores the data in Redis for display

    :return:
    """
    def _scrape_quickplay_data(response, player):
        # Scrapes Most played hero
        most_played_hero = response.text[response.text.find('akamaihd.net/hero/'):].split('/')[2]
        player[1]['most_played_hero'] = most_played_hero
        player[1]['portrait'] = 'img/portrait/{}.png'.format(most_played_hero)

        # Scrapes level
        player[1]['level'] = int(response.text[response.text.find('<div class="u-vertical-center'):].split('>')[1][:-5])

        # Scrapes level frame image URL
        #player[1]['level_frame_img_url'] = response.text[response.text.find('playerlevelrewards') - 45:].split('(')[1].split(')')[0]
        player[1]['level_frame_img_url'] = response.text[response.text.find('class="player-level"') - 100:].split('(')[1].split(')')[0]

        # Scrapes rank image URL
        if response.text.find('class="player-rank"') > 0:
            player[1]['rank_img_url'] = response.text[response.text.find('class="player-rank"') - 100:].split('(')[1].split(')')[0]

        #############################################################################################################
        ##### Below scraping won't work if the player is new, all the calculation based on scraping goes below ######

        # Scrapes and calculates winrate
        if response.text.find('Games Won', 70000) == -1:
            player[1]['games_won'] = 0
            player[1]['games_played'] = 0
            return player

        games_won = response.text[response.text.find('Games Won', 70000):].split("</td>")[1][4:].replace(',', '')
        games_played = response.text[response.text.find('Games Played', 70000):].split("</td>")[1][4:].replace(',', '')
        player[1]['games_won'] = int(games_won)
        player[1]['games_played'] = int(games_played)
        player[1]['winrate'] = '{:.1f}'.format(float(games_won)/float(games_played) * 100)

        # Scrapes and calculates KDA
        defensive_assists = 0
        if response.text.find('<td>Defensive Assists</td>') != -1:
            defensive_assists = response.text[response.text.find('<td>Defensive Assists</td>'):].split('</td>')[1][4:].replace(',', '')
        offensive_assists = 0
        if response.text.find('<td>Offensive Assists</td>') != -1:
            offensive_assists = response.text[response.text.find('<td>Offensive Assists</td>'):].split('</td>')[1][4:].replace(',', '')


        kills = response.text[response.text.find('<td>Eliminations</td>'):].split('</td>')[1][4:].replace(',', '')
        deaths = response.text[response.text.find('<td>Deaths</td>'):].split('</td>')[1][4:].replace(',', '')
        player[1]['kills'] = kills
        player[1]['offensive_assists'] = offensive_assists
        player[1]['defensive_assists'] = defensive_assists
        player[1]['deaths'] = deaths
        player[1]['kda'] = '{:.2f}'.format((float(defensive_assists) + float(offensive_assists) + float(kills)) / float(deaths))

        # Scrapes and calculates Card/game
        player[1]['cards'] = response.text[response.text.find('Match Awards'):].split('<td>')[2].split('<')[0].replace(',', '')
        player[1]['card_rate'] = '{:.2f}'.format(float(player[1]['cards']) / float(games_played) * 100)

        # Scrapes and calculates Medal/game
        player[1]['medals'] = response.text[response.text.find('Match Awards'):].split('<td>')[4].split('<')[0].replace(',', '')
        player[1]['medal_per_game'] = '{:.2f}'.format(float(player[1]['medals']) / float(games_played))

        return player

    def _scrape_competitive_data(response, player):
        player[1]['competitive_skill_rating'] = response.text[response.text.find('competitive-rank') + 15:].split('<')[2].split('>')[1].split('<')[0]
        player[1]['competitive_skill_rating_img'] = response.text[response.text.find('competitive-rank') + 15:].split('<')[1].split('"')[1]

        competitive_context = response.text[response.text.find('<div id="competitive-play">'):]

        competitive_games_won = competitive_context[competitive_context.find('Games Won</td>'):].split("<td>")[1].split('<')[0].replace(',', '')
        competitive_games_played = competitive_context[competitive_context.find('Games Played</td>'):].split("<td>")[1].split('<')[0].replace(',', '')
        player[1]['competitive_games_won'] = int(competitive_games_won)
        player[1]['competitive_games_played'] = int(competitive_games_played)
        player[1]['competitive_winrate'] = '{:.1f}'.format(float(competitive_games_won)/float(competitive_games_played) * 100)

        # Scrapes and calculates KDA
        competitive_defensive_assists = 0
        if competitive_context.find('<td>Defensive Assists</td>') != -1:
            competitive_defensive_assists = competitive_context[competitive_context.find('<td>Defensive Assists</td>'):].split('</td>')[1][4:].replace(',', '')
        competitive_offensive_assists = 0
        if competitive_context.find('<td>Offensive Assists</td>') != -1:
            competitive_offensive_assists = competitive_context[competitive_context.find('<td>Offensive Assists</td>'):].split('</td>')[1][4:].replace(',', '')


        competitive_kills = competitive_context[competitive_context.find('<td>Eliminations</td>'):].split('</td>')[1][4:].replace(',', '')
        competitive_deaths = competitive_context[competitive_context.find('<td>Deaths</td>'):].split('</td>')[1][4:].replace(',', '')
        player[1]['competitive_kills'] = competitive_kills
        player[1]['competitive_offensive_assists'] = competitive_offensive_assists
        player[1]['competitive_defensive_assists'] = competitive_defensive_assists
        player[1]['competitive_deaths'] = competitive_deaths
        player[1]['competitive_kda'] = '{:.2f}'.format((float(competitive_defensive_assists) + float(competitive_offensive_assists) + float(competitive_kills)) / float(competitive_deaths))

        return player

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