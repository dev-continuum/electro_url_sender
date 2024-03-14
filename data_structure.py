from enum import Enum


class ChargeModFixedData(Enum):
    """
    https://github.com/ocpi/ocpi/blob/master/version_information_endpoint.asciidoc#125-versionnumber-enum
    """
    VENDOR_ID = "chargemod"
    LOCATION_VERB = 'stations'
    START_CHARGE_VERB = 'charging/start'
    STOP_CHARGE_VERB = 'charging/stop'
    CHARGE_ACTIVITY_VERB = 'charging/activities'


class ChargeModDeviceStatus(Enum):
    healthy = 'healthy'
    not_connected = 'not_connected'
    under_voltage = 'under_voltage'
    over_voltage = 'over_voltage'
    over_current = 'over_current'
    network_disconnected = 'network_disconnected'
    power_failed = 'power_failed'
    over_temperature = 'over_temperature'


class ChargerStatus(Enum):
    CHARGER_AVAILABLE = "AVAILABLE"
    CHARGER_BUSY = "BUSY"
    CHARGER_NOT_WORKING = "FAULTY"
    CHARGER_BOOKED = "BOOKED"
    CHARGER_RESERVED = "RESERVED"


