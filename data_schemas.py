from data_structure import ChargeModFixedData, ChargeModDeviceStatus
from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, Dict, List
from decimal import Decimal


class ChargeModLocationsUrls(BaseModel):
    base_url: str
    vendor_id: Optional[ChargeModFixedData] = ChargeModFixedData.VENDOR_ID.value
    verb: Optional[ChargeModFixedData] = ChargeModFixedData.LOCATION_VERB.value
    call_method: Optional[str] = "GET"

    class Config:
        use_enum_values = True


class ChargeModHeader(BaseModel):
    Accept: str
    key: str
    Authorization: str
    class Config:
        use_enum_values = True


class ChargeModLocationsParams(BaseModel):
    q: str
    filter_status: Optional[str] = "Available"
    name: Optional[str] = None
    model: Optional[str] = None
    rate: Optional[str] = None
    image: Optional[str] = None
    timings: Optional[str] = None
    sockets: Optional[str] = None
    vehicle_types: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    state: Optional[str] = None
    device_status: Optional[ChargeModDeviceStatus] = None
    station_id: Optional[str] = None

    class Config:
        use_enum_values = True


class ChargeModStartChargeUrls(BaseModel):
    base_url: str
    vendor_id: Optional[ChargeModFixedData] = ChargeModFixedData.VENDOR_ID.value
    verb: Optional[ChargeModFixedData] = ChargeModFixedData.START_CHARGE_VERB.value
    call_method: Optional[str] = "POST"

    class Config:
        use_enum_values = True


class ChargeModStartChargeParams(BaseModel):
    station_id: str
    reference_transaction_id: str
    user_id: str
    relay_switch_number: str
    max_energy_consumption: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    rate: Optional[str] = None
    image: Optional[str] = None
    timings: Optional[str] = None
    sockets: Optional[str] = None
    vehicle_types: Optional[str] = None
    address: Optional[str] = None


class ChargeModStopChargeUrls(BaseModel):
    base_url: str
    vendor_id: Optional[ChargeModFixedData] = ChargeModFixedData.VENDOR_ID.value
    verb: Optional[ChargeModFixedData] = ChargeModFixedData.STOP_CHARGE_VERB.value
    call_method: Optional[str] = "POST"

    class Config:
        use_enum_values = True


class ChargeModStopChargeParams(BaseModel):
    reference_transaction_id: str
    id: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    rate: Optional[str] = None
    image: Optional[str] = None
    timings: Optional[str] = None
    sockets: Optional[str] = None
    vehicle_types: Optional[str] = None
    address: Optional[str] = None


class ChargeModChargingActivityUrls(BaseModel):
    base_url: str
    vendor_id: Optional[ChargeModFixedData] = ChargeModFixedData.VENDOR_ID.value
    verb: Optional[ChargeModFixedData] = ChargeModFixedData.CHARGE_ACTIVITY_VERB.value
    call_method: Optional[str] = "GET"


class ChargeModChargeActivityParams(BaseModel):
    id: Optional[str] = None


class ChargingStationStaticData(BaseModel):
    station_id: str
    vendor_id: str
    name: str
    address_line: str
    town: str
    state: str
    postal_code: str
    latitude: Decimal
    longitude: Decimal
    country: str
    qr_code: Optional[str] = None
    total_connectors_available: int
    station_status: ChargeModDeviceStatus
    station_time: Optional[Dict] = None
    distance_unit: Optional[int] = None
    is_ocpp: Optional[bool] = False
    total_charger_data: List
    expanded_total_charger_data: List
    image: Optional[AnyHttpUrl] = None
    geo_address: List
    uid: Optional[str] = None,
    rating: Dict = {"avg_rating": 0,
                    "5": 0,
                    "4": 0,
                    "3": 0,
                    "2": 0,
                    "1": 0,
                    }

    class Config:
        use_enum_values = True




