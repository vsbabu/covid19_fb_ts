# this works as the task automator using doit
# run as either `doit` from this folder or
# as `python -m doit`

from doit.tools import create_folder

BUILD_PATH = "output"


def task_get_daily_csv():
    def transform(dependencies, targets):
        from etl import json_to_csv

        json_to_csv(
            src=dependencies[0],
            target=targets[0],
            field_expressions=[
                """$.cases_time_series[*].date""",
                """$.cases_time_series[*].dailyconfirmed""",
                """$.cases_time_series[*].dailyrecovered""",
                """$.cases_time_series[*].dailydeceased""",
            ],
            field_names=["dt", "confirmed", "recovered", "deceased"],
            # input date is like dd Mm; make it dd-Mm-yyyy assuming 2020
            field_massager=lambda x: (x[1] + " 2020").replace(" ", "-") if x[0] == 0 else x[1],
        )

    return {
        "targets": ["%s/daily.csv" % BUILD_PATH],
        "file_dep": ["%s/daily.json" % BUILD_PATH],
        "actions": [transform],
    }


def task_get_daily_json():
    def extract(dependencies, targets):
        from etl import get_json

        get_json("https://api.covid19india.org/data.json", targets[0])

    return {
        "targets": ["%s/daily.json" % BUILD_PATH],
        "file_dep": ["%s/.wip" % BUILD_PATH],
        "actions": [extract],
    }


def task_build():
    return {
        "actions": [(create_folder, [BUILD_PATH]), "touch %(targets)s"],
        "targets": ["%s/.wip" % BUILD_PATH],
    }
