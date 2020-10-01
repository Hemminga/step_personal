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
    table = soup.find('table', class_='data')
    _data = {}
    key = ''
    for tr in table.children:
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
                        row['declarer'] = td.text
                    if index == 4:
                        row['points'] = td.text
                    if index == 5:
                        row['score'] = td.text

                    index += 1
                else:
                    continue
            results.append(row)
    return results


def process_details(_data):
    print(_data.name)
    _tables = _data.td.find_all('table', recursive=False)
    # details = []
    tables = []
    for table in _tables:
        print(type(table))
        if type(table) == element.NavigableString:
            continue
        tables.append(table)
    for table in tables:
        index = 0
        for td in table.tbody.tr.children:
            if index == 0:
                # This table contains the game
                pass
            else:
                # This table contains the board results
                pass
            if type(td) == element.NavigableString:
                continue
            print(td.name)
            index +=1