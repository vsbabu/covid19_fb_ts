import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
import json

import csv
from jsonpath_ng import jsonpath, parse


FILE_CACHE_DIR = ".web_cache"


def json_to_csv(
    src, target, field_expressions=[], field_names=None, field_massager=None
):
    """
    Convert a json to csv.
    Arguments:
        src {[file]} -- input json file
        target {[file]} -- output csv file

    Keyword Arguments:
        field_expressions {list} -- jsonpath-ng expressions (default: {[]} which is useless)
                you've to give expression for each column. JSON Path allows things
                like one expression for somepath[*].[f1, f2, f3], but getting it out
                as one sub-array of f1,f2,f3 row is very ugly code. This way, we will
                burn some CPU for getting each column as an array and then zip it all up.
        field_names {list} -- a list of field headings to be added to the CSV
        field_massager {func} -- a function that modifies a row before it is written
    """
    with open(src, "r") as json_file:
        json_data = json.load(json_file)
    holds = []
    for expr in field_expressions:
        col = []
        jsonpath_expression = parse(expr)
        for match in jsonpath_expression.find(json_data):
            col.append(match.value.strip())
        holds.append(col)
    result = zip(*holds)
    result = list(result)
    with open(target, "w") as csvo:
        wr = csv.writer(csvo, quoting=csv.QUOTE_MINIMAL)
        if field_names is not None:
            wr.writerow(field_names)
        for row in result:
            if field_massager is not None:
                row = list(map(field_massager, enumerate(row)))
            wr.writerow(row)


def get_json(src, target):
    sess = CacheControl(requests.session(), cache=FileCache(FILE_CACHE_DIR))
    response = sess.get(src)
    jsond = response.json()
    with open(target, "w") as outfile:
        json.dump(jsond, outfile)


if __name__ == "__main__":
    get_json(src="https://api.covid19india.org/data.json", target="output/daily.json")
    json_to_csv(
        src="output/daily.json",
        target="output/daily.csv",
        field_expressions=[
            """$.cases_time_series[*].date""",
            """$.cases_time_series[*].dailyconfirmed""",
            """$.cases_time_series[*].dailyrecovered""",
            """$.cases_time_series[*].dailydeceased""",
        ],
        field_names=["dt", "confirmed", "recovered", "deceased"],
    )
