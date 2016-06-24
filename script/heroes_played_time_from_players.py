import re, operator
import requests, json


REDIS_URL = "chriss-fun-1.office.airg.lan"
overwatch_url = 'https://playoverwatch.com/en-us/career/pc/us/{}'

players = [
    ('Ben', {'handle': 'Trillium-1317'}),
    ('Chris', {'handle': 'musa-1521'}),
    ('Lee', {'handle': 'Taystamah-1107'}),
    ('Allen', {'handle': 'alhole-1287'}),
    ('Edward', {'handle': 'pigeon-1559'}),
    ('Akibo', {'handle': 'Akibo-1700'}),
    ('Fuggles', {'handle': 'fuggles-1605'})
]

heroes = {}

def main():
    for player in players:
        response = requests.get(overwatch_url.format(player[1]['handle']))

        for m in re.finditer('hours</div>', response.text):
            hero = response.text[m.start()-50:m.end()].split('>')[1].split('<')[0].encode('utf-8')
            hours = int(response.text[m.start()-5:m.start()].split('>')[1].strip())
            minutes = hours * 60

            if heroes.get(hero):
                heroes[hero] += minutes
            else:
                heroes[hero] = minutes

        for m in re.finditer('hour</div>', response.text):
            hero = response.text[m.start()-50:m.end()].split('>')[1].split('<')[0].encode('utf-8')
            minutes = 60

            if heroes.get(hero):
                heroes[hero] += minutes
            else:
                heroes[hero] = minutes

        for m in re.finditer('minutes</div>', response.text):
            hero = response.text[m.start()-50:m.end()].split('>')[1].split('<')[0].encode('utf-8')
            minutes = int(response.text[m.start()-5:m.start()].split('>')[1].strip())

            if heroes.get(hero):
                heroes[hero] += minutes
            else:
                heroes[hero] = minutes

    sorted_result = sorted(heroes.items(), key=operator.itemgetter(1), reverse=True)

    for item in sorted_result:
        print '{}: {} hours'.format(item[0], '{:.2f}'.format(float(item[1]) / 60))

    return


if __name__ == "__main__":
    main()