import re
from pprint import pprint


def save_lin(_details, _data, username):
    boards_text = _details['Spellen']
    pattern = re.compile(r'\((\d+) x (\d+)\)')
    match = pattern.search(boards_text)
    boards_each_round = 0
    rounds = 0
    if match:
        boards_each_round = match.group(2)
        rounds = match.group(1)
    boards = int(rounds) * int(boards_each_round)
    print(boards)

    if _details['Speelvorm'] == 'Paren':
        # Other option is 'I' for IMPs but that seem to be Teams only
        # P is for Pairs with MP scoring
        _format = 'P'

    tournament_name = 'De Zeerob ' + _details['Gespeeld']
    detail_name = username
    # For the subtitle: find partner of `username`
    if _data[0]['bidding']['East']['player'] == username:
        partner = _data[0]['bidding']['West']['player']
    if _data[0]['bidding']['West']['player'] == username:
        partner = _data[0]['bidding']['East']['player']
    if _data[0]['bidding']['North']['player'] == username:
        partner = _data[0]['bidding']['South']['player']
    if _data[0]['bidding']['South']['player'] == username:
        partner = _data[0]['bidding']['North']['player']
    if partner:
        detail_name = username + ' - ' + partner

    # .lin label |vg|
    # Event name `tournament name`
    # Detail name
    # 'P' or 'I' `_format`
    # start board
    # number of boards
    # Team 1 name
    # Team 1 starting IMPS
    # Team 2 name
    # Team 2 starting points
    vg = f'{tournament_name},{detail_name},P,1,28,Team1,0,Team2,0'

    # .lin label |rs|
    # Contracts separated by comma. Don't forget to add a blank after each board, e.g. ... ,2H=,, ...
    rs = []
    # .lin label |pw|
    # List with pair names. Leave blank in places where there is no change
    pw = []
    # .lin lable |mp|
    # Table with IMP scores (also leave the second blank)
    mp = []
    # .lin label |bn|
    # Board numbers
    # Most likely this is only used if the boards are not in order
    bn = []

    # First cycle for vugraph meta data
    for b in _data:
        # Add board number to list
        if 'board' in b and 'number' in b['board']:
            bn.append(b['board']['number'])
        else:
            # This works out to skip boards that are not played
            continue
        # Players SWNE
        pw.append(b['bidding']['South']['player'])
        pw.append(b['bidding']['West']['player'])
        pw.append(b['bidding']['North']['player'])
        pw.append(b['bidding']['East']['player'])
        pw = pw + ['', '', '', '']
        rs.append(b['play']['result']['level']
                  + b['play']['result']['suit']
                  + b['play']['result']['declarer']
                  + ('=' if b['play']['result']['result'] == 'C' else b['play']['result']['result']))
        rs.append('')
        # Score (IMP) is always in from the players perspective
        # We want to rework that into NS score (IMP)
        reverse_scoring = False
        score = int(b['play']['score']['value'])
        if username in [b['bidding']['East'], b['bidding']['West']]:
            reverse_scoring = True
        if reverse_scoring:
            score = 1 - score
        mp.append(str(score))
        mp.append('')
    print('vg|' + vg + '|')
    print('rs|' + ','.join(rs) + '|')
    print('pw|' + ','.join(pw) + '|')
    print('mp|' + ','.join(mp) + '|')
    print('bn|' + ','.join(bn) + '|')
    print('pg||')

    # Second cycle for individual game data
    index_round = 0
    index_board = 0
    seats = ['South', 'West', 'North', 'East']
    # In the board details section of the .lin file, the declarer is 'South' or first mentioned.
    pn = []
    for b in _data:
        declarer = b['play']['result']['declarer']
        pn.append(declarer)

        index_board += 1
        if index_board % int(boards_each_round) == 0:
            index_board = 0
            index_round += 1