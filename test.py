import json
import unittest
from lambda_function import map_chargemod_to_electrolite_structure, call_handle_chargemod_exception, third_party_caller, \
    parse_sns_message_process, lambda_handler
import data_schemas
from http import HTTPStatus

class MyTestCase(unittest.TestCase):
    charge_mod_data1 = {
        "id": 110,
        "station_type_id": 1,
        "name": "BB Test",
        "phone": "01122334455",
        "email": "hello@chargemod.com",
        "street1": "chargemod",
        "street2": "Down Town City Vista",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "zip": "411014",
        "latitude": 8.561339,
        "longitude": 76.911983,
        "image": "https://testnet.chargemod.com//storage/stations/station.jpg",
        "status": 1,
        "device_status": "Healthy",
        "is_blackbox": 1,
        "is_listed": "false",
        "is_free": 1,
        "qr_code": "CM-S00110-NIBFC96LOS",
        "device_id": "987654321",
        "device_uuid": "987654321",
        "last_message_received_at": "2022-08-20 07:40:04",
        "last_battery_low_alert_at": "null",
        "created_at": "2022-02-28 12:14:06",
        "updated_at": "2022-08-20 07:40:04",
        "deleted_at": "null",
        "provider": "null",
        "available_pins_count": 1,
        "is_owner": "false",
        "charging_pins": [{
            "id": 1,
            "name": "BlackBox",
            "battery": "240VAC, 15A",
            "type": "AC",
            "status": 1,
            "created_at": "2020-01-14 10:56:00",
            "updated_at": "2021-08-13 02:37:58",
            "deleted_at": "null",
            "image": "3dda06f2-2204-4c5a-aaab-d02d8d2beac7.png",
            "image_url": "https://testnet.chargemod.com//storage/charging-pins/3dda06f2-2204-4c5a-aaab-d02d8d2beac7.png",
            "pivot": {
                "station_id": 110,
                "charging_pin_id": 1,
                "id": 151,
                "available": 1,
                "status": 1,
                "relay_switch_number": 1,
                "step_size": "null"
            }
        },
            {
                "id": 2,
                "name": "BlackBox",
                "battery": "240VAC, 15A",
                "type": "AC",
                "status": 2,
                "created_at": "2020-01-14 10:56:00",
                "updated_at": "2021-08-13 02:37:58",
                "deleted_at": "null",
                "image": "3dda06f2-2204-4c5a-aaab-d02d8d2beac7.png",
                "image_url": "https://testnet.chargemod.com//storage/charging-pins/3dda06f2-2204-4c5a-aaab-d02d8d2beac7.png",
                "pivot": {
                    "station_id": 110,
                    "charging_pin_id": 1,
                    "id": 151,
                    "available": 2,
                    "status": 2,
                    "relay_switch_number": 1,
                    "step_size": "null"
                }
            }
        ],
        "station_type": {
            "id": 1,
            "name": "BlackBox",
            "marker": "dca9a6f2-a533-45ff-a171-ea6594b4b497.png",
            "created_at": "2021-02-26T07:01:42.000000Z",
            "updated_at": "2021-02-26T07:06:16.000000Z",
            "marker_url": "https://testnet.chargemod.com//storage/station-types/dca9a6f2-a533-45ff-a171-ea6594b4b497.png"
        }
    }

    def setUp(self) -> None:
        self.header_data = dict(data_schemas.ChargeModHeader.parse_obj({
            "Accept": "application/json",
            "key": "chargeMod_g0MODf3n11p5cZSpPCVylKvDXyn9JD",
            "Authorization": "Bearer Qp9yqzHff0DvYlgGHemD1TIsTfTDCoev"
        }))


    def test_lambda_handler_parsing(self):
        payload = {"vendor_id": "chargemod", "action": "start_charge",
                   "write": False,
                   "base_url": "https://apitest.chargemod.com",
                   "params": {
                          "station_id": 113,
                          "reference_transaction_id": 404112718119,
                            "user_id": 12,
                            "relay_switch_number": 111,
                            "max_energy_consumption": 10
                   },
                   "header": {
                       "Accept": "application/json",
                       "key": "chargeMod_g0MODf3n11p5cZSpPCVylKvDXyn9JD",
                       "Authorization": "Bearer Qp9yqzHff0DvYlgGHemD1TIsTfTDCoev"
                   }}
        print(json.dumps(payload))
        lambda_handler(event=json.dumps(payload), context={})
    def test_data_parsing(self):
        result = None
        result = map_chargemod_to_electrolite_structure(self.charge_mod_data1).json()
        print(result)
        self.assertTrue(result)

    def test_chargemod_location_url_sending(self):
        url_data = data_schemas.ChargeModLocationsUrls.parse_obj({"base_url": "https://apitest.chargemod.com"})

        request_params = dict(data_schemas.ChargeModLocationsParams.parse_obj({
            "q": "BB"
        }))
        result = call_handle_chargemod_exception(url_data=url_data, request_params=request_params,
                                                 header_data=self.header_data)
        self.assertEqual(result["status_code"], HTTPStatus.OK)
        #print(result["data"])
        data_to_write = result["data"]
        parsed_station_data = []
        for station in data_to_write:
            station["vendor_id"] = "chargemod"
            parsed_station_data.append(map_chargemod_to_electrolite_structure(station).json())
        print(parsed_station_data)

    def test_chargemod_start_charging_url(self):
        url_data = data_schemas.ChargeModStartChargeUrls.parse_obj({"base_url": "https://apitest.chargemod.com"})

        request_params = dict(data_schemas.ChargeModStartChargeParams.parse_obj({
            "station_id": 110,
            "reference_transaction_id": 71,
            "user_id": 12,
            "relay_switch_number": 111,
            "max_energy_consumption": 10
        }))
        response = call_handle_chargemod_exception(url_data, self.header_data, request_params)
        print(response)

    def test_chargemod_stop_charging_url(self):
        url_data = data_schemas.ChargeModStopChargeUrls.parse_obj({"base_url": "https://apitest.chargemod.com"})
        request_params = dict(data_schemas.ChargeModStopChargeParams.parse_obj({
            "reference_transaction_id": 3
        }))
        call_handle_chargemod_exception(url_data, self.header_data, request_params)

    def test_chargemod_activity_charging_url(self):
        url_data = data_schemas.ChargeModChargingActivityUrls.parse_obj({"base_url": "https://apitest.chargemod.com"})
        request_params = dict(data_schemas.ChargeModChargeActivityParams.parse_obj({
            "reference_transaction_id": 1
        }))
        call_handle_chargemod_exception(url_data, request_params=None, header_data=self.header_data, path=1)



if __name__ == '__main__':
    unittest.main()
