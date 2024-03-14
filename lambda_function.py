import json
import boto3
import logging
import requests
import string
import secrets
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr, BeginsWith, Contains
import data_schemas
from data_structure import ChargerStatus
from urllib.parse import urljoin
from http import HTTPStatus

'''
This lambda function will work as url sender
It will get requests from user apis 
they will provide a definition of task
Based on that, function will first generate an appropriate URL and then send the request. 
It will return the response accordingly
'''

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def third_party_caller(url_data, request_params, header, path: str):
    try:
        final_url = urljoin(url_data.base_url, url_data.verb)
        if path:
            final_url = final_url + f"/{path}"
        logging.info(f"final url is {final_url}")
        logging.info(f"{request_params}")
        logging.info(f"{header}")
        response = requests.request(method=url_data.call_method, url=final_url,
                                    data=request_params, headers=header, verify=False)
        logging.info(f"Response after call is {response}")
    except AttributeError:
        logging.exception("error in sending request")
        return False
    else:
        try:
            return response.json()
        except Exception:
            return False

def parse_expanded_chargemod_total_chargers(chargers) -> []:
    parsed_list_of_chargers = []
    for charger_point in chargers:
        parsed_list_of_chargers.append({"charger_point_id": charger_point["id"],
                                        "charger_point_type": charger_point["type"],
                                        "power_capacity": charger_point["battery"],
                                        "charger_point_status": translate_status_to_text(charger_point["status"]),
                                        "connector_point_id": charger_point["pivot"]["charging_pin_id"],
                                        "tariff": 125
                                        })

    return parsed_list_of_chargers

def parse_chargemod_total_chargers(chargers) -> []:
    parsed_list_of_chargers = []
    charger_id = set()
    for charger_point in chargers:
        if charger_point["id"] not in charger_id:
            # first insert logic
            charger_id.add(charger_point["id"])
            parsed_list_of_chargers.append({"charger_point_id": charger_point["id"],
                                            "charger_point_type": charger_point["type"],
                                            "power_capacity": charger_point["battery"],
                                            "charger_point_status": translate_status_to_text(charger_point["status"]),
                                            "connectors": [
                                                {"connector_point_id": charger_point["pivot"]["charging_pin_id"],
                                                 "relay_number": charger_point["pivot"]["relay_switch_number"],
                                                 "status": translate_status_to_text(charger_point["pivot"]["status"]),
                                                 "tariff": 125
                                                 }]
                                            })
        else:
            # append logic if evse id already exist
            for charger in parsed_list_of_chargers:
                if charger["charger_point_id"] == charger_point["id"]:
                    charger["connectors"].append({"connector_point_id": charger_point["pivot"]["charging_pin_id"],
                                                  "relay_number": charger_point["pivot"]["relay_switch_number"],
                                                  "status": charger_point["pivot"]["status"],
                                                  "tariff": 125
                                                  })
    return parsed_list_of_chargers


def translate_status_to_text(status):
    if status == 1:
        return ChargerStatus.CHARGER_AVAILABLE
    else:
        return ChargerStatus.CHARGER_BUSY

def map_chargemod_to_electrolite_structure(station):
    try:
        parsed_total_chargemod_data = parse_chargemod_total_chargers(station["charging_pins"])
        count_of_chargers = len(parsed_total_chargemod_data)

        mapper = {
            "station_id": station["id"],
            "vendor_id": "chargemod",
            "name": station["name"],
            "address_line": station["street1"],
            "town": station["city"],
            "state": station["state"],
            "postal_code": station["zip"],
            "latitude": station["latitude"],
            "longitude": station["longitude"],
            "country": station["country"],
            "qr_code": station["qr_code"],
            "total_connectors_available": count_of_chargers,
            "station_status": station["device_status"].lower(),
            "station_time": {"start_time": "12:00 AM", "end_time": "11:59 PM"},
            "geo_address": [station["latitude"], station["longitude"]],
            "image": station["image"],
            "total_charger_data": parsed_total_chargemod_data,
            "expanded_total_charger_data": parse_expanded_chargemod_total_chargers(station["charging_pins"])
        }
    except KeyError:
        raise
    else:
        return data_schemas.ChargingStationStaticData.parse_obj(mapper)


def call_handle_chargemod_exception(url_data, request_params, header_data, path=None):
    response = third_party_caller(url_data, request_params, header_data, path)
    if not response:
        return {"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": "No response from station",
                "data": {}}
    else:
        try:
            response["data"]
        except KeyError:
            logging.exception(f"Response does not have any data"
                              f"Dumping response {response}")
            return {"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": response["message"],
                    "data": {}}
        except Exception:
            logging.exception(f"Unknown response Dumping response {response}")
            return {"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": "No response from station",
                    "data": {}}
        else:
            if response["success"]:
                return {"status_code": HTTPStatus.OK, "message": response["message"],
                        "data": response["data"]}
            else:
                return {"status_code": HTTPStatus.SERVICE_UNAVAILABLE, "message": response["message"],
                        "data": response["data"]}


def parse_sns_message_process(message_in_event):
    logging.info(f"message in event is {message_in_event}")
    requests_params = None
    url_data = None
    parsed_station_data = []
    if message_in_event["vendor_id"].lower() == "chargemod" and message_in_event["action"].lower() == "location":
        # Parse params with chargemod location pydantic class
        request_params = dict(data_schemas.ChargeModLocationsParams.parse_obj(message_in_event["params"]))
        url_data = data_schemas.ChargeModLocationsUrls.parse_obj({"base_url": message_in_event["base_url"]})
        header_data = dict(data_schemas.ChargeModHeader.parse_obj(message_in_event["header"]))
        logging.info(f"Got request params {request_params}")
        logging.info(f"Got url dat {url_data}")
        if url_data:
            response = call_handle_chargemod_exception(url_data, request_params, header_data)
            if response["status_code"] == HTTPStatus.OK and message_in_event["write"]:
                # Renaming id to station id as this is more readable in db. it's a primary key
                data_to_write = response["data"]
                for station in data_to_write:
                    # ----------- adding vendor sort key here ----------------------
                    station["vendor_id"] = message_in_event["vendor_id"]
                    parsed_station_data.append(map_chargemod_to_electrolite_structure(station).json())
                requests.post(os.environ['DB_API'],
                              json={"write_vendor_data_to_location_table": True,
                                    "data_to_write": parsed_station_data})
            elif response["status_code"] == HTTPStatus.OK:
                return response
            else:
                return {"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": "Unknown Error",
                        "data": {}}

    elif message_in_event["vendor_id"].lower() == "chargemod" and message_in_event["action"].lower() == "start_charge":
        request_params = dict(data_schemas.ChargeModStartChargeParams.parse_obj(message_in_event["params"]))
        url_data = data_schemas.ChargeModStartChargeUrls.parse_obj({"base_url": message_in_event["base_url"]})
        header_data = dict(data_schemas.ChargeModHeader.parse_obj(message_in_event["header"]))
        return call_handle_chargemod_exception(url_data, request_params, header_data)

    elif message_in_event["vendor_id"].lower() == "chargemod" and message_in_event["action"].lower() == "stop_charge":
        request_params = dict(data_schemas.ChargeModStopChargeParams.parse_obj(message_in_event["params"]))
        url_data = data_schemas.ChargeModStopChargeUrls.parse_obj({"base_url": message_in_event["base_url"]})
        header_data = dict(data_schemas.ChargeModHeader.parse_obj(message_in_event["header"]))
        return call_handle_chargemod_exception(url_data, request_params, header_data)

    elif message_in_event["vendor_id"].lower() == "chargemod" and message_in_event["action"].lower() == "activities":
        path = dict(data_schemas.ChargeModChargeActivityParams.parse_obj(message_in_event["params"]))["id"]
        url_data = data_schemas.ChargeModChargingActivityUrls.parse_obj({"base_url": message_in_event["base_url"]})
        header_data = dict(data_schemas.ChargeModHeader.parse_obj(message_in_event["header"]))
        return call_handle_chargemod_exception(url_data, request_params=None, header_data=header_data, path=path)
    else:
        logging.warning(f"There is no match for this event. Here is the event dump {message_in_event}")


def lambda_handler(event, context):
    logging.info(f"here is the event {event}")
    try:
        event["vendor_id"]
    except KeyError:
        message_in_event = json.loads(event['Records'][0]['Sns']['Message'])
    else:
        message_in_event = event

    return parse_sns_message_process(message_in_event)
