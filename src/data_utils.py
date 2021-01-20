import csv
import os
from datetime import datetime, timedelta

def write_to_csv(save_fp, record, header=[]):
    if os.path.exists(save_fp):
        is_newlog = False
    else:
        is_newlog = True

    if is_newlog:
        write_option = 'w'
        with open(save_fp, mode=write_option,
                  encoding='UTF-8-sig') as log_file:
            log_writer = csv.writer(log_file,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            if len(header) > 1:
                log_writer.writerow(header)
                log_writer.writerow([x for x in record])
            else:
                log_writer.writerow([x for x in record])
    else:
        write_option = 'a'
        with open(save_fp, mode=write_option,
                  encoding='UTF-8-sig') as log_file:
            log_writer = csv.writer(log_file,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)

            log_writer.writerow([x for x in record])


def format_search_date_str(base_date_str, days_diff=15):
    base_date_obj = datetime.strptime(base_date_str, '%Y/%m/%d')
    start_date_obj = base_date_obj - timedelta(days=15)
    end_date_obj = base_date_obj + timedelta(days=15)

    start_date_str = start_date_obj.date().strftime('%Y%m%d')
    end_date_str = end_date_obj.date().strftime('%Y%m%d')

    return start_date_str, end_date_str