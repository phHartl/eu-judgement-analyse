import os
import xmltodict
import json

def dump_to_files(data, dump_type, iteration_num):
    counter = 0
    subdirectory = ''
    file_prefix = dump_type + '_'
    iter_directory = 'iter_' + str(iteration_num) + '/'

    if dump_type == 'parse':
        subdirectory = '/parse_dumps/'
    elif dump_type == 'response':
        subdirectory = '/response_dumps/'
    else:
        print('FILE SAVER: invalid dump_type')
        return -1

    dump_directory = os.path.dirname(__file__) + subdirectory
    if not os.path.exists(dump_directory):
        os.mkdir(dump_directory)
    if not os.path.exists(dump_directory + iter_directory):
        os.mkdir(dump_directory + iter_directory)

    for item in data:
        item['date'] = str(item.get('date'))
        json_data = json.dumps(item, indent=4)
        with open(dump_directory + iter_directory + file_prefix + str(counter) +'.json', 'w') as json_file:
            json_file.write(json_data)
            json_file.close()
        counter += 1