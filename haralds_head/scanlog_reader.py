#!/usr/bin/env python3
import json

class HaraldsJsonReader(object):

    def __init__(*args, **kwargs):
        pass

    @staticmethod
    def read_scanlog_json():
        try:
            with open('/opt/haralds-head/scans/haralds-scanlog.txt', 'r') as f:
                results_items = f.read()
        except Exception as err:
            print(err)
            return []

        # clear empty items
        results_items = list(filter(None, results_items.split('\n')))

        # newest first
        results_items.reverse()

        # format fake json items
        fake_json_items = ','.join(results_items)

        # format json array
        fake_json_array = '{"results": [' + fake_json_items + ']}'

        # read json from string
        results_json = json.loads(fake_json_array)
        return results_json


if __name__ == '__main__':
    json = HaraldsJsonReader.read_scanlog_json()
    print(json)
