import model
from pprint import pprint

activityid = 17972
username = "FoppeHe"


if __name__ == '__main__':
    data = model.get_data(activityid, username)
    data_tables = model.get_data_table(data)
    tables = model.extract_data(data_tables)
    pprint(len(tables))
    # tables[0] contains info about the data
    # tables[1] is the first header 'Overzicht Resultaten'
    # tables[2] is the results table
    # tables[3] is the second header 'Details per Spel'
    # tables[4] is the details table
    meta = model.get_metadata(activityid)
    pprint(meta)
    results = model.process_results(tables[2])
    pprint(results)
