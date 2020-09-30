import model
from pprint import pprint

activityid = 17972
username = "FoppeHe"


if __name__ == '__main__':
    data = model.get_data(activityid, username)
    data_tables = model.get_data_table(data)
    tables = model.extract_data(data_tables)
    pprint(len(tables))
    # tables[0] contains indo about the data
    # tables[2] is the first header 'Overzicht Resultaten'
    # tables[3] is the results table
    # tables[4] is the second header 'Details per Spel'
    # tables[5] is the details table
