#!/usr/bin/env python3

import os
from wyze_sdk import Client
from wyze_sdk.models.devices import plugs
from wyze_sdk.errors import WyzeApiError
from datetime import datetime, timedelta, timezone
import pytz
import json

with open('wyze_config.json', 'r') as config_file:
    config = json.load(config_file)
    WYZE_EMAIL = config['WYZE_EMAIL']
    WYZE_PASSWORD = config['WYZE_PASSWORD']
    WYZE_API_KEY_ID = config['WYZE_API_KEY_ID']
    WYZE_API_KEY = config['WYZE_API_KEY']
    OUTLET_MAC_ADDRESS = config['OUTLET_MAC_ADDRESS'] #currently not used

if WYZE_EMAIL == "youremail@domain.com":
    print("Please update wyze_config.json with your Wyze credentials.")
    exit(1)

response = Client().login(email=WYZE_EMAIL, password=WYZE_PASSWORD, key_id=WYZE_API_KEY_ID, api_key=WYZE_API_KEY)

client = Client(token=response['access_token'])

date_string_start = input("Enter a start date in YYYY-MM-DD format: ")
try:
    start_date = datetime.strptime(date_string_start, "%Y-%m-%d")
except ValueError:
    print("Invalid date format. Please use YYYY-MM-DD.")

date_string_end = input("Enter an end date in YYYY-MM-DD format: ")
try:
    end_date = datetime.strptime(date_string_end, "%Y-%m-%d")
except ValueError:
    print("Invalid date format. Please use YYYY-MM-DD.")

print()

def get_outlet_power_usage(start_date, end_date):
    if not client:
        print("Client is not initialized due to authentication failure.")
        return None

    try:
        # Fetch all plugs
        devices = client.plugs.list()
        # Iterate through all devices
        for device in devices:
            #print(f"mac: {device.mac}")
            #print(f"nickname: {device.nickname}")
            #print(f"is_online: {device.is_online}")
            #print(f"product model: {device.product.model}")

            # Check if the device matches the specified MAC address or is an outdoor plug
            try:
                # Fetch electricity consumption record
                total_usage = 0
                #print(f"Plug: {device.nickname} (MAC: {device.mac} Start: {start_date} End: {end_date})")
                consumption_record = client.plugs.get_usage_records(device_mac=device.mac, device_model=device.product.model, start_time=start_date)
                #print(f"Electricity Consumption Record for {device.nickname}: {consumption_record}")
                #for test in consumption_record:
                #    print(f"Test: {test}")
                for record in consumption_record:
                    record_date, not_a_date = record.hourly_data.popitem()
                    r_date_only = record_date.date()
                    #print(f'Record Date {record_date}, Start Date {start_date} End Date {end_date}')
                    if r_date_only <= end_date.date():
                        #print(f"Record Date: {r_date_only}")
                        #print(f"Record Total Usage: {record.total_usage}")
                        total_usage += record.total_usage
                print(f"Total Usage for {device.nickname}: {total_usage} kWh")
            except AttributeError:
                print(f"PlugElectricityConsumptionRecord not valid function for {device.nickname}.")
            except WyzeApiError as e:
                print(f"Failed to retrieve power usage for {device.nickname}: {e}")
            print("-" * 40)

    except WyzeApiError as e:
        print(f"Failed to retrieve devices: {e}")
        return None

#testing & debugging code
#start_date = datetime(2025, 4, 6)
#print(f"Start Date: {start_date}")
#print(f"End Date: {end_date}")
#end_date = datetime(2025, 4, 8)
#start_date.replace(tzinfo=pytz.timezone('US/Pacific'))
#print(f"Start Date PST: {start_date}")
#end_date.replace(tzinfo=timezone)
#start date isn't inclusive, so subtract by 1 day
start_date = start_date - timedelta(days=1)
get_outlet_power_usage(start_date,end_date)