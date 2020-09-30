import requests


def get_data(_activityid, _username):
    url = 'http://admin.stepbridge.nl/show.php?page='
    url += f'tournamentinfo&activityid={_activityid}&username={_username}'
    _data = requests.get(url)
    return _data
