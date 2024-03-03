#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2023, 2024 Kuopio Hacklab
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
#
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
