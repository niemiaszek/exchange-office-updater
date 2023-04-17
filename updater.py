#!/usr/bin/env python3
from pathlib import Path
import requests
import datetime
import os
import time
import json
from dotenv import load_dotenv


def process_variable(variable: str, currency_rates) -> bool:
    """Parse variable from file into api accepted format

    Example of line in file: "$EURku='4.6700';". Example of variable requested by API: "🇪🇺 EUR Buy":"4.67".
    """

    name_mapping = {
        "EUR": "🇪🇺 EUR",
        "USD": "🇺🇸 USD",
        "CHF": "🇨🇭 CHF",
        "GBP": "🇬🇧 GBP",
        "CAD": "🇨🇦 CAD",
        "AUD": "🇦🇺 AUD",
        "SEK": "🇸🇪 SEK",
        "NOK": "🇳🇴 NOK",
        "DKK": "🇩🇰 DKK",
        "UAH": "🇺🇦 UAH",
        "BGN": "🇧🇬 BGN",
        "HUF": "🇭🇺 HUF",
        "CZK": "🇨🇿 CZK",
        "RON": "🇷🇴 RON",
    }

    type_mapping = {"ku": " Buy", "sp": " Sell"}
    name, value = variable.split("=")

    currency_name = name[1:-2]
    if currency_name == "HRK" or currency_name == "EUB":  # HRK is not longer supported by webpage
        return False

    final_name = name_mapping[name[1:-2]] + type_mapping[name[-2:]]
    final_value = float(value[1:-3])

    currency_rates[final_name] = final_value
    return True


def main():
    load_dotenv()
    filepath = Path("KURWAL.PHP")
    updated_time = time.time()  # init last updated time to program startup time
    file_time = None
    err_counter = 0

    while True:
        file_time = os.path.getmtime(filepath)
        print(file_time, updated_time)
        if file_time <= updated_time: # if file wasnt updated since last update made by program
            time.sleep(10)
            continue
        else:
            updated_time = file_time


        try:
            with open(filepath, "r") as f:
                file_contents = f.readlines()
            err_counter = 0
        except IOError as err:  # If file got deleted or is currently open by another process
            print(err)
            err_counter += 1
            if err_counter >= 5:
                break

            time.sleep(1)
            continue

        currency_rates = {}
        for line in file_contents:
            if not ("ku" in line or "sp" in line):  # If line doesn't reference any currency rate
                continue
            process_variable(line, currency_rates)

        url = os.environ.get('API_URL')
        headers = {"updater-secret": os.environ.get('UPDATER_SECRET')}
        r = requests.post(url, json=currency_rates, headers=headers)
        print(r)





if __name__ == "__main__":
    main()
