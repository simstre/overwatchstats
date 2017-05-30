from app.constants import RANK_IMAGE_LIST


def _scrape_quickplay_data(response, player):
    # Scrapes Most played hero
    most_played_hero = response.text[response.text.find('data-hero-competitive'):].split('"')[1]
    if not most_played_hero:
        most_played_hero = response.text[response.text.find('data-hero-quickplay'):].split('"')[1]
    player[1]['most_played_hero'] = most_played_hero
    player[1]['portrait'] = 'img/portrait/{}.png'.format(most_played_hero)

    # Scrapes level
    player[1]['level'] = int(response.text[response.text.find('<div class="u-vertical-center'):].split('>')[1][:-5])

    # Scrapes level frame image URL
    player[1]['level_frame_img_url'] = response.text[response.text.find('class="player-level"') - 100:].split('(')[1].split(')')[0]
    level_img_starting_index = player[1]['level_frame_img_url'].find('0x0')
    level_img_ending_index = player[1]['level_frame_img_url'].find('_Border.png')
    level_img_hex_value = player[1]['level_frame_img_url'][level_img_starting_index:level_img_ending_index]
    if int(level_img_hex_value, 16) > int('0x0250000000000955', 16):
        player[1]['level'] += 600

    # Scrapes rank image URL
    if response.text.find('class="player-rank"') > 0:
        player[1]['rank_img_url'] = response.text[response.text.find('class="player-rank"') - 100:].split('(')[1].split(')')[0]
        for rank_img_tuple in RANK_IMAGE_LIST:
            for image_url in rank_img_tuple[0]:
                if player[1]['rank_img_url'].find(image_url) > 0:
                    player[1]['level'] += rank_img_tuple[1]

    #############################################################################################################
    ##### Below scraping won't work if the player is new, all the calculation based on scraping goes below ######

    # Scrapes and calculates winrate
    if response.text.find('Games Won', 70000) == -1:
        player[1]['games_won'] = 0
        player[1]['games_played'] = 0
        return player

    games_won = response.text[response.text.find('<td>Games Won</td>', 2500):].split("</td>")[1][4:].replace(',', '')
    # Since they removed this, gotta hack to figure it out using one of the stats
    # I'm using damage done
    #games_played = response.text[response.text.find('Games Played', 70000):].split("</td>")[1][4:].replace(',', '')
    damage_done = response.text[response.text.find('<td>Damage Done</td>'):].split('<td>')[2][:-14].replace(',', '')
    avg_damage_done = response.text[response.text.find('<td>Damage Done - Average</td>'):].split('<td>')[2][:-14].replace(',', '')
    games_played = int(int(damage_done) / int(avg_damage_done))

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

    competitive_context = response.text[response.text.find('<div id="competitive"'):]

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

    # Scrapes and calculates Card/game
    player[1]['competitive_cards'] = competitive_context[competitive_context.find('Match Awards'):].split('<td>')[2].split('<')[0].replace(',', '')
    player[1]['competitive_card_rate'] = '{:.2f}'.format(float(player[1]['competitive_cards']) / float(competitive_games_played) * 100)

    # Scrapes and calculates Medal/game
    player[1]['competitive_medals'] = competitive_context[competitive_context.find('Match Awards'):].split('<td>')[4].split('<')[0].replace(',', '')
    player[1]['competitive_medal_per_game'] = '{:.2f}'.format(float(player[1]['competitive_medals']) / float(competitive_games_played))

    return player