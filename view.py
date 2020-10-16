import math
import re
from pprint import pprint


def save_lin(_details, _data):
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
        # Other option is 'I' for IMPs (teams and pairs?)
        # Found B for board-a-match
        # P is for Pairs with MP scoring
        _format = 'I'

    tournament_name = 'De Zeerob ' + _details['Gespeeld']
    username = _data[0]['perspective']['username']
    detail_name = username  # default
    # For the subtitle: find partner of `username`
    partner = ''
    if _data[0]['bidding']['East']['player'] == username:
        partner = _data[0]['bidding']['West']['player']
    if _data[0]['bidding']['West']['player'] == username:
        partner = _data[0]['bidding']['East']['player']
    if _data[0]['bidding']['North']['player'] == username:
        partner = _data[0]['bidding']['South']['player']
    if _data[0]['bidding']['South']['player'] == username:
        partner = _data[0]['bidding']['North']['player']
    if partner:
        detail_name = username + (' - ' + partner if partner else '')

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

    filename = f"./{tournament_name.replace(' ', '_').replace(':', '')}.lin"
    with open(filename, 'w') as f:
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
                      + b['play']['result']['suit'][0]  # Shorten NT to N
                      + b['play']['result']['declarer'][0]
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
            # @TODO |mp| is MP score according to tenace. Will it work with IMP?
            mp.append('')
        f.write('vg|' + vg + '|\n')
        f.write('rs|' + ','.join(rs) + '|\n')
        f.write('pw|' + ','.join(pw) + '|\n')
        f.write('mp|' + ','.join(mp) + '|\n')
        f.write('bn|' + ','.join(bn) + '|\n')
        f.write('pg||\n')

        # Second cycle for individual game data
        index_round = 0
        index_board = 0
        seats = ['South', 'West', 'North', 'East']
        # In the board details section of the .lin file, the declarer is 'South' or first mentioned.
        for b in _data:
            if 'play' not in b:
                continue
            board_number = int(b['board']['number'])
            f.write('qx|o' + str(board_number) + '|\n')
            pn = []
            declarer = b['play']['result']['declarer']
            pn.append(b['bidding'][declarer]['player'])
            index = seats.index(declarer)
            pn.append(b['bidding'][seats[(index + 1) % 4]]['player'])
            pn.append(b['bidding'][seats[(index + 2) % 4]]['player'])
            pn.append(b['bidding'][seats[(index + 3) % 4]]['player'])
            f.write('pn|' + ','.join(pn) + '|')
            f.write('rh||')  # Reset header
            f.write('ah|' + 'Board ' + str(board_number) + '|')  # Board name
            dealer = declarer[(board_number-1) % 4]
            vuln_table = ['0', 'n', 'e', 'b']
            vulnerable = vuln_table[((board_number-1) % 16 + math.floor(board_number / 4)) % 4]
            f.write('sv|' + vulnerable + '|')
            f.write('pg||\n')

            # The number before the first suit letter indicates the dealer: 1=South, 2=West, 3=North, 4=East
            board_starts_with = seats.index(b['board']['dealer']) + 1
            hands = ''
            for seat in seats:
                hand = 'S{}H{}D{}C{}'.format(
                    b['board'][seat]['spades'],
                    b['board'][seat]['hearts'],
                    b['board'][seat]['diamonds'],
                    b['board'][seat]['clubs']
                )
                hands += hand + ','
            f.write(f'md|{board_starts_with}{hands[0:-1]}|')
            em = b['play']['score']['value']
            f.write(f"em|{b['perspective']['direction']} {em}|")
            f.write('pg||\n')
            # print(f"len(b['play']['play']): {len(b['play']['play'])}")

            # Bidding
            for bid in b['bidding']['bids']:
                if bid['empty']:
                    continue
                f.write(f"mb|{bid['rank']}{bid['suit'][0]}|")
                if bid['alert']:
                    f.write('an|*|')
            f.write('pg||\n')

            # Play
            for i in range(52):
                if 1 != 52 and len(b['play']['play']) == i:
                    f.write('pg||\n')
                    break
                f.write(f"pc|{b['play']['play'][i]['suit']}{b['play']['play'][i]['rank']}|")
                if i % 4 == 3:
                    f.write('pg||\n')
            if b['play']['tricks']['EW'] + b['play']['tricks']['NS'] < 13:
                f.write(f"mc|{b['play']['tricks']['claim']}|")
            index_board += 1
            if index_board % int(boards_each_round) == 0:
                index_board = 0
                index_round += 1