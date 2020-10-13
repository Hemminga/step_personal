import model
import view
from pprint import pprint

activityid = 17972
username = "FoppeHe"


if __name__ == '__main__':
    # Event data
    tables = model.get_metadata(activityid)
    event_details = model.process_event(tables[0])
    pprint(event_details)
    # Pairs
    standings = []
    if len(tables) > 1:
        for table in tables[1:]:
            standings += model.process_standings(table)
    # pprint(standings)
    # Board data
    data = model.get_data(activityid, username)
    data_tables = model.get_data_table(data)
    tables = model.extract_data(data_tables)
    # pprint(f'{len(tables)} tables')  # 5
    # tables[0] contains info about the data
    # tables[1] is the first header 'Overzicht Resultaten'
    # tables[2] is the results table
    # tables[3] is the second header 'Details per Spel'
    # tables[4] is the details table

    # 2020-10-03: Decided against using the results table
    # Reason: gathering the same data from the details will
    # have benefit of adding the lead.
    # results = model.process_results(tables[2])
    # pprint(results)
    boards, results = model.process_details(tables[4])
    # pprint(boards[0])
    view.save_lin(event_details, boards)
