import re
import requests
from bs4 import BeautifulSoup, element
# from pprint import pprint


def get_data(_activity_id, _username):
    url = 'http://admin.stepbridge.nl/show.php?page='
    url += f'tournamentinfo&activityid={_activity_id}&username={_username}'
    _data = requests.get(url)

    return _data.content


def get_data_table(_data):
    soup = BeautifulSoup(_data, 'html.parser')
    return soup.table.find('table')


def extract_data(_soup):
    tables = []
    trs = _soup.table
    for tr in trs.children:
        if type(tr) != element.NavigableString:
            if tr.name == 'tr':
                # print(type(tr))
                # print(tr.name)
                tables.append(tr)
    return tables


def get_metadata(_activity_id):
    """
    This function gets the tournament meta data from the
    parent page. It does all everything in this small function,
    the request and the extraction of data through BeautifulSoup.
    :param _activity_id:
    :return: dictionary with tournament meta data
    """
    url = 'http://admin.stepbridge.nl/show.php?page='
    url += f'tournamentinfo&activityid={_activity_id}'
    _data = requests.get(url)
    soup = BeautifulSoup(_data.content, 'html.parser')
    tables = soup.find_all('table', class_='data')
    return tables


def process_event(_event):
    _data = {}
    key = ''
    for tr in _event.children:
        if tr.name == 'col':
            continue
        if type(tr) != element.NavigableString:
            trs = tr.find_all('td')
            index = 0
            for td in trs:
                if index % 2 == 1:
                    _data[key] = td.text.replace('\xa0\xa0', ' ')
                else:
                    key = td.text[:-1]
                index += 1
    return _data


def process_standings(_data):
    standings = []
    index = 0
    for tr in _data.tbody.children:
        if type(tr) == element.NavigableString:
            if not tr.isspace():
                print(tr)
            continue
        collect = {}
        for td in tr.children:
            if type(td) == element.NavigableString:
                if not td.isspace():
                    print(td)
                continue
            if index == 0:
                collect['rank'] = td.text[:-1]
                index += 1
                continue
            if index == 1:
                players = td.text.split('-')
                collect['player1'] = players[0].strip()
                collect['player2'] = players[1].strip()
                index += 1
                continue
            if index == 2:
                # @TODO split this into a number and a unit
                collect['score'] = td.text
                standings.append(collect)
                index = 0
    return standings


def process_results(_data):
    _table = _data.find('table')
    # print(_table.prettify())
    results = []
    for tr in _table.tbody.children:
        if type(tr) != element.NavigableString:
            index = 0
            row = {}
            for td in tr.children:
                if type(td) != element.NavigableString:
                    if index == 0:
                        row['spel'] = td.text
                    if index == 1:
                        if td.text == 'spel niet gespeeld':
                            row['contract'] = '-'
                            row['result'] = '-'
                            row['declarer'] = '-'
                            row['points'] = '-'
                            row['lead'] = '-'
                            row['score'] = '-'
                            break
                        else:
                            # @TODO CHeck this with all possible input
                            color = td.contents[0].strip().replace('SA', 'NT')[1:]
                            if len(td.contents) > 1:
                                color = td.contents[1]['alt']
                            if len(td.contents) > 2:
                                # X or XX
                                color += td.contents[2]
                            row['contract'] = td.text.strip()[0] + color
                    if index == 2:
                        row['result'] = td.text
                    if index == 3:
                        row['side'] = td.text.replace('Z', 'S').replace('O', 'E')
                    if index == 4:
                        row['points'] = td.text
                    if index == 5:
                        # @TODO Check this with all possible input
                        score = td.text.split(' ')
                        row['score'] = score[0]
                        row['score_type'] = score[1]

                    index += 1
                else:
                    continue
            results.append(row)
    return results


def process_details(_data):
    _tables = _data.td.find_all('table', recursive=False)
    # details = []
    tables = []
    boards = []
    results = []
    pattern = re.compile('Spel (\d+)\s+\(')
    board_number = 0
    for table in _tables:
        if type(table) == element.NavigableString:
            continue
        tables.append(table)
    for table in tables:
        index = 0

        for td in table.tbody.tr.children:
            if type(td) == element.NavigableString:
                if not td.isspace():
                    print(td)
                continue
            if index == 0:
                # This table contains the game
                meta = table.thead.tr.find('th', class_='boardheaderleft')
                # print(meta.text)
                match = pattern.search(meta.text)
                if match:
                    board_number = match.group(1)
                boards.append(process_game_data(td, board_number))
            else:
                # This table contains the board results
                results.append(process_results_data(td))
            index += 1
    return boards, results


def translate_seat(seat):
    english = ''
    if seat == 'N':
        english = 'North'
    elif seat == 'O':
        english = 'East'
    elif seat == 'Z':
        english = 'South'
    elif seat == 'W':
        english = 'West'
    else:
        print(f"Unknown error. Seat = {seat} and this program will fail shortly ;)")
    return english


def process_game_data(_data, _number):
    if len(_data.contents) == 2:
        print("Board not played")
        # @TODO We can process the board here
        return {}

    # @TODO Split in three separate functions
    board_table = _data.contents[1]
    bidding_table = _data.contents[5]
    # play_table = _data.contents[9]

    # Process board_table
    rows = []
    for tr in board_table.children:
        if type(tr) == element.NavigableString:
            if not tr.isspace():
                print(tr)
            continue
        if tr.name == 'col':
            continue
        rows.append(tr)
    # But it rotates the board so the designated player is always south
    board = {'number': _number, 'North': {}, 'East': {}, 'South': {}, 'West': {}}
    meta = rows[0].contents[1].text.split('/')
    board['dealer'] = translate_seat(meta[0])
    board['vulnerable'] = meta[1]
    # print(rows[0].contents)
    # print(rows[1].contents)
    player_data = rows[0].contents[3].text.split(' - ')
    seat = translate_seat(player_data[0])
    board[seat]['name'] = player_data[1]
    board[seat]['seat'] = seat
    board[seat]['spades'] = rows[1].contents[3].text.strip()
    board[seat]['hearts'] = rows[2].contents[3].text.strip()
    board[seat]['diamonds'] = rows[3].contents[3].text.strip()
    board[seat]['clubs'] = rows[4].contents[3].text.strip()
    player_data = rows[4].contents[5].text.split(' - ')
    seat = translate_seat(player_data[0])
    board[seat]['name'] = player_data[1]
    board[seat]['seat'] = seat
    board[seat]['spades'] = rows[5].contents[5].text.strip()
    board[seat]['hearts'] = rows[6].contents[5].text.strip()
    board[seat]['diamonds'] = rows[7].contents[5].text.strip()
    board[seat]['clubs'] = rows[8].contents[5].text.strip()
    player_data = rows[4].contents[1].text.split(' - ')
    seat = translate_seat(player_data[0])
    board[seat]['name'] = player_data[1]
    board[seat]['seat'] = seat
    board[seat]['spades'] = rows[5].contents[1].text.strip()
    board[seat]['hearts'] = rows[6].contents[1].text.strip()
    board[seat]['diamonds'] = rows[7].contents[1].text.strip()
    board[seat]['clubs'] = rows[8].contents[1].text.strip()
    player_data = rows[8].contents[3].text.split(' - ')
    seat = translate_seat(player_data[0])
    board[seat]['name'] = player_data[1]
    board[seat]['seat'] = seat
    board[seat]['spades'] = rows[9].contents[3].text.strip()
    board[seat]['hearts'] = rows[10].contents[3].text.strip()
    board[seat]['diamonds'] = rows[11].contents[3].text.strip()
    board[seat]['clubs'] = rows[12].contents[3].text.strip()

    # Process bidding table
    head = bidding_table.thead
    # WIP
    # body = bidding_table.body

    # The header of the table reveals the seat and the players' names
    bidding = {'number': _number, 'North': {}, 'South': {}, 'East': {}, 'West': {},
               'dealer': board['dealer']}
    index = 0
    seats = []
    for seat in head.children:
        if type(seat) == element.NavigableString:
            if not seat.isspace():
                print(seat)
            continue
        for tr in seat.children:
            if type(tr) == element.NavigableString:
                if not tr.isspace():
                    print(tr)
                continue

            if index < 4:
                seat = translate_seat(tr.text)
                seats.append(seat)
                bidding[seat]['seat'] = seat
            else:
                assert 4 <= index < 8
                bidding[seats[index-4]]['player'] = tr.text
            index = (index + 1) % 8

    start = meta[0]  # Dealer in the original language
    return {'board': board, 'bidding': bidding}


def process_results_data(_data):
    # WIP
    # results_table = _data.contents[1]
    return {}
