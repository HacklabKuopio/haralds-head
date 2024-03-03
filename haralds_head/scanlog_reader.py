#!/usr/bin/env python3
import json


class HaraldsJsonReader(object):

    def __init__(*args, **kwargs):
        pass

    @staticmethod
    def read_fake_json():
        ### SAMPLE 1
        with open('/opt/haralds-head/scans/disobey-scanlog.txt', 'r') as f:
            results_items = f.read()

        # clear empty items
        results_items = list(filter(None, results_items.split('\n')))

        results_items.reverse()

        # format fake json items
        fake_json_items = ','.join(results_items)

        # format json array
        fake_json_array = '{"results": [' + fake_json_items + ']}'
        # print(fake_json_array)

        # read json from string
        results_json = json.loads(fake_json_array)
        return results_json


#    @staticmethod
#    def read_json():
#        ### SAMPLE 2
#        with open('/opt/haralds-head/scans/disobey-scanlog.json', 'r') as f:
#            results_json = json.load(f)
#            return results_json
#

if __name__ == '__main__':
    json1 = HaraldsJsonReader.read_fake_json()
    json2 = HaraldsJsonReader.read_json()

    print(json1)
    print(json2)



