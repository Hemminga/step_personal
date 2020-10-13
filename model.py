import re
import requests
from bs4 import BeautifulSoup, element
from pprint import pprint


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
                board = {}
                # This table contains the game
                meta = table.thead.tr.find('th', class_='boardheaderleft')
                # print(meta.text)
                match = pattern.search(meta.text)
                if match:
                    board_number = match.group(1)

                # Big work happening here
                board_table, bidding_table, play_table = process_game_data(td)
                _dealer = ''
                if board_table:
                    board_data = process_board_table(board_table, board_number)
                    _dealer = board_data['dealer']
                    board['board'] = board_data
                if bidding_table:
                    bidding_data = process_bidding_table(bidding_table, board_number, _dealer)
                    board['bidding'] = bidding_data
                if play_table:
                    play_data, inner_play_table = extract_play_meta(play_table)
                    # Note that we are passing the play_data dict to the next stage
                    # to gather all information in one place
                    play_data = process_play_table(inner_play_table, play_data, board_data)
                    board['play'] = play_data
            else:
                # This table contains the board results
                results, par = process_results_data(td)
                # pprint(results)
                board['results'] = {'results': results, 'par': par}
                boards.append(board)
            index += 1
    return boards


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


def process_game_data(_data):
    if len(_data.contents) == 2:
        # print("Board not played")
        # @TODO We can process the board here
        return {}, {}, {}

    board_table = _data.contents[1]
    bidding_table = _data.contents[5]
    play_table = _data.contents[9]
    return board_table, bidding_table, play_table


def process_board_table(board_table, _number):
    # Process board_table
    rows = []
    trans = str.maketrans('HVB', 'KQJ')
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
    board[seat]['spades'] = rows[1].contents[3].text.strip().translate(trans)
    board[seat]['hearts'] = rows[2].contents[3].text.strip().translate(trans)
    board[seat]['diamonds'] = rows[3].contents[3].text.strip().translate(trans)
    board[seat]['clubs'] = rows[4].contents[3].text.strip().translate(trans)
    player_data = rows[4].contents[5].text.split(' - ')
    seat = translate_seat(player_data[0])
    board[seat]['name'] = player_data[1]
    board[seat]['seat'] = seat
    board[seat]['spades'] = rows[5].contents[5].text.strip().translate(trans)
    board[seat]['hearts'] = rows[6].contents[5].text.strip().translate(trans)
    board[seat]['diamonds'] = rows[7].contents[5].text.strip().translate(trans)
    board[seat]['clubs'] = rows[8].contents[5].text.strip().translate(trans)
    player_data = rows[4].contents[1].text.split(' - ')
    seat = translate_seat(player_data[0])
    board[seat]['name'] = player_data[1]
    board[seat]['seat'] = seat
    board[seat]['spades'] = rows[5].contents[1].text.strip().translate(trans)
    board[seat]['hearts'] = rows[6].contents[1].text.strip().translate(trans)
    board[seat]['diamonds'] = rows[7].contents[1].text.strip().translate(trans)
    board[seat]['clubs'] = rows[8].contents[1].text.strip().translate(trans)
    player_data = rows[8].contents[3].text.split(' - ')
    seat = translate_seat(player_data[0])
    board[seat]['name'] = player_data[1]
    board[seat]['seat'] = seat
    board[seat]['spades'] = rows[9].contents[3].text.strip().translate(trans)
    board[seat]['hearts'] = rows[10].contents[3].text.strip().translate(trans)
    board[seat]['diamonds'] = rows[11].contents[3].text.strip().translate(trans)
    board[seat]['clubs'] = rows[12].contents[3].text.strip().translate(trans)
    return board


def process_bidding_table(bidding_table, _number, _dealer):
    # Process bidding table
    bidding = {'number': _number, 'North': {}, 'South': {}, 'East': {}, 'West': {},
               'dealer': _dealer, 'first_seat': ''}

    def process_bidding_header(_head):
        # The header of the table reveals the seat and the players' names
        index = 0
        seats = []
        for seat in _head.children:
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
                    if index == 0:
                        bidding['first_seat'] = seat
                    bidding[seat]['seat'] = seat
                else:
                    assert 4 <= index < 8
                    bidding[seats[index-4]]['player'] = tr.text
                index = (index + 1) % 8

    def process_bidding_body(_body):
        _first_seat = bidding['first_seat']
        hands = ['North', 'East', 'South', 'West']
        index = hands.index(_first_seat)
        # This gives the list of hands in the same order as the (bidding) table
        hands = [hands[(index+x) % 4] for x in range(len(hands))]
        # print(f'index: {index}, hands: {hands}, fist_seat: {_first_seat}')
        index_round = 0
        bids = []
        for tr in _body.children:
            if type(tr) == element.NavigableString:
                if not tr.isspace():
                    print(tr)
                continue
            index_hand = 0
            for td in tr.children:
                if type(td) == element.NavigableString:
                    if not td.isspace():
                        print(td)
                    continue
                bid = {'round': index_round+1,
                       'order': index_hand+1,
                       'hand': hands[index_hand],
                       'alert': False,
                       'empty': False}
                _alt = ''
                try:
                    _alt = td.contents[1]['alt']
                except KeyError:
                    # td.contents may have no img and therefore no alt tag
                    pass
                except TypeError:
                    # td.contents[3].img may not exist and give a 'NoneType' TypeError
                    pass
                except AttributeError:
                    pass
                except IndexError:
                    pass
                double = ''
                if _alt:
                    suit = _alt
                elif 'pas' in td.text:
                    suit = 'pass'
                elif 'SA' in td.text:
                    suit = 'NT'
                elif 'dbl' in td.text:
                    double = 'X'
                elif 'rdbl' in td.text:
                    double = 'XX'
                elif '-' in tr.text:
                    suit = ''
                    bid['empty'] = True
                else:
                    suit = ''
                    bid['empty'] = True
                if '*' in td.text:
                    bid['alert'] = True
                rank = ''
                if td.text[0].isdigit():
                    rank = td.text[0]
                # print(f"{rank}{suit}{('*' if bid['alert'] else '')} {double}")
                bid['rank'] = rank
                bid['suit'] = suit
                bid['double'] = double
                bids.append(bid)
                index_hand += 1
            index_round += 1
        # pprint(bids)
        bidding['bids'] = bids

    head = bidding_table.thead
    process_bidding_header(head)
    # print(bidding_table)
    body = bidding_table.tbody
    process_bidding_body(body)

    return bidding


def extract_play_meta(play_table):
    """
    This function receives the Play table and returns
    a dict with some meta data plus the inner table that
    contains the actual Play.
    :param play_table:
    :return: dict, BeautifulSoup object
    """
    play = {}
    for td in play_table.children:
        if type(td) == element.NavigableString:
            if not td.isspace():
                print(td)
            continue
        if 'Slagen:' in td.text:
            break
        _alt = ''
        if len(td.contents) > 3 and td.contents[3].text:
            try:
                _alt = td.contents[3].img['alt']
            except KeyError:
                # td.contents may have no img and therefore no alt tag
                pass
            except TypeError:
                # td.contents[3].img may not exist and give a 'NoneType' TypeError
                pass
            split_line = td.contents[3].text.split(' ', 1)
            td.contents[3] = split_line[0] + _alt + ' ' + split_line[1]
        if 'Resultaat:' in td.text:
            play['result'] = td.contents[3]
        elif 'Score:' in td.text:
            play['score'] = td.contents[3]
    # Prepare the inner table with Play data for further processing
    _table = play_table.find('table')
    return play, _table


def process_play_table(play_table, play_data, board_data):
    tricks = []
    trans = str.maketrans('HVBOZ', 'KQJEW')
    for tr in play_table.children:
        if type(tr) == element.NavigableString:
            if not tr.isspace():
                print(tr)
            continue
        if tr.name == 'col':
            continue
        index = 0
        trick_number = 1
        trick = []
        for td in tr.children:
            card = {}
            if type(td) == element.NavigableString:
                if not td.isspace():
                    print(td)
                continue
            # print(f'{index}: {td}')
            if index == 0:
                trick_number = td.text[:-1]
                index += 1
                continue
            else:
                try:
                    # Board may not be played
                    # Trick may not be finished due to claim
                    suit = td.contents[0]['alt']
                    rank = td.text.translate(trans)
                    card['trick'] = trick_number
                    card['suit'] = suit
                    card['rank'] = rank
                    card['seat'] = in_hand({'suit': suit, 'rank': rank, 'board': board_data})
                    tricks.append(card)
                except AttributeError:
                    continue
                except TypeError:
                    continue
            index += 1
    # pprint(tricks)
    play_data['play'] = tricks
    return play_data


def in_hand(_data):
    """
    Determines in which hand a given card is.
    :param _data: Dictionary with keys 'suit', 'rank' and 'board'
    :return: Enum 'N', 'E', 'S', 'W'
    """
    suit = 'spades'
    if _data['suit'] == 'H':
        suit = 'hearts'
    if _data['suit'] == 'D':
        suit = 'diamonds'
    if _data['suit'] == 'C':
        suit = 'clubs'
    if _data['rank'] in _data['board']['North'][suit]:
        return 'N'
    if _data['rank'] in _data['board']['East'][suit]:
        return 'E'
    if _data['rank'] in _data['board']['South'][suit]:
        return 'S'
    if _data['rank'] in _data['board']['West'][suit]:
        return 'W'
    return None


def process_results_data(_data):
    trans = str.maketrans('HVBOZ', 'KQJEW')
    results_table = _data.contents[1].tbody
    results = []
    # pprint(results_table.tbody)
    for tr in results_table.children:
        if type(tr) == element.NavigableString:
            if not tr.isspace():
                print(tr)
            continue
        if tr.name == 'col':
            continue
        index = 0
        result = {}
        for td in tr.children:
            if type(td) == element.NavigableString:
                if not td.isspace():
                    print(td)
                continue
            if index == 0:
                result['leader'] = td.text
            elif index == 1:
                suit = 'pass'
                double = ''
                try:
                    suit = td.contents[1]['alt']
                except TypeError:
                    if 'SA' in td.text:
                        suit = 'SA'
                except IndexError:
                    if 'SA' in td.text:
                        suit = 'SA'
                if 'X' in td.text:
                    double = 'X'
                if 'XX' in td.text:
                    double = 'XX'
                result['contract'] = {'contract': td.text[0] + suit + double,
                                      'level': td.text[0],
                                      'suit': suit,
                                      'double': double}
            elif index == 2:
                result['result'] = td.text
            elif index == 3:
                result['compass'] = td.text.translate(trans)
            elif index == 4:
                try:
                    suit = td.contents[0]['alt']
                except TypeError:
                    suit = ''
                except IndexError:
                    suit = ''
                result['lead'] = {'lead': suit + td.text.translate(trans),
                                  'suit': suit,
                                  'value': td.text.translate(trans)}
            elif index == 5:
                result['points'] = td.text
            elif index == 6:
                result['score'] = td.text
                results.append(result)
            index += 1
    par = calculate_par(results)
    # pprint(results)
    return results, par


def calculate_par(_results):
    """
    Calculate par for Butler type scoring
    :param _results:
    :return:
    """
    scores = []
    for result in _results:
        scores.append(int(result['points']))
    scores.sort()
    if len(scores) == 0:
        return 0
    # Remove highest and lowest score
    # Bij 1 t/m 3 scores wordt er niets weggelaten, bij 4 of 5 scores worden de twee buitenste score
    # voor de helft meegenomen in de weging, bij 6 of meer scores worden de hoogste en laagste 10% van
    # de scores weggelaten.
    if 3 < len(scores) < 6:
        scores = [scores[0]] + scores[1:-1] + scores[1:-1] + [scores[-1]]
    else:
        treshold = round(len(scores) / 10)
        scores = scores[treshold:-treshold]
    avg = int(sum(scores) / len(scores) / 10) * 10
    # print(f'Butlerscore: {avg}')
    return avg
