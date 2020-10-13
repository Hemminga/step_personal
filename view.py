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

    tournament_name = 'De Zeerob ' + _details['Gespeeld']
    round = 0
    _format = 'I'
    if _details['Speelvorm'] == 'Paren':
        # Other option is 'I' for IMPs but that seem to be Teams only
        # P is for Pairs with MP scoring
        _format = 'P'
