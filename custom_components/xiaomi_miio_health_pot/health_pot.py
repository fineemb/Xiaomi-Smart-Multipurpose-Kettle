import enum
import logging
from typing import Any, Dict, Optional

import click

from .click_common import EnumType, command, format_output
from miio import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_HEALTH_POT_1 = "viomi.health_pot.v1"

AVAILABLE_STATE = {
    0 : "stopped",
    1 : "reservation",
    2 : "cooking",
    3 : "paused",
    4 : "keeping",
    5 : "stop"
}

AVAILABLE_MODE = {
    11 : "Herbal tea",
    12 : "Fruit tea",
    13 : "Simmered soup",
    14 : "Medicinal food",
    15 : "Congee",
    16 : "Edible bird's nest",
    17 : "Hotpot",
    18 : "Boiled water",
    19 : "Warm milk",
    20 : "Soft-boiled egg",
    21 : "Yogurt",
    22 : "Steamed egg",
    23 : "brewed_tea",
    24 : "Ganoderma",
    25 : "Disinfect",
    26 : "Sweet soup", 
    1  : "Custom1",
    2  : "Custom2",
    3  : "Custom3", 
    4  : "Custom4", 
    5  : "Custom5", 
    6  : "Custom6", 
    7  : "Custom7", 
    8  : "Custom8" 
}

AVAILABLE_RUN_STATUS = {
    0 :  "On base",
    16 : "No kettle placed",
    32 : "Drycooking protection",
    48 : "Both"
}

AVAILABLE_PROPERTIES_COMMON = [
    "run_status",
    "work_status",
    "warm_data",
    "last_time",
    "last_temp",
    "curr_tempe",
    "work_temps",
    "mode",
    "heat_power",
    "warm_time",
    "cook_time",
    "left_time",
    "cook_status",
    "cooked_time",
    "voice",
    "stand_top_num",
    "mode_sort"
]

SUPPORTED_MODELS = {
    MODEL_HEALTH_POT_1: {
        "available_properties": AVAILABLE_PROPERTIES_COMMON
#        "last_temp": (40, 95),
#        "last_time": (0, 12 * 3600),
    }
}

class Health_PotException(DeviceException):
    pass

class Health_PotStatus:
    """Container for status reports from the Xiaomi Mijia Multifunctional."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Health_Pot (viomi.health_pot.v1):
        {'power': 'off', 'target_temperature': 24, 'brightness': 1,
        'buzzer': 'on', 'child_lock': 'off', 'temperature': 22.3,
        'use_time': 43117, 'poweroff_time': 0, 'relative_humidity': 34}
        """
        self.data = data

    @property
    def run_status(self) -> Optional[str]:
        """Current run_status."""
        if (
            "run_status" in self.data
            and self.data["run_status"] is not None
        ):
            return AVAILABLE_RUN_STATUS[int(self.data["run_status"])]

        return None
    
    @property
    def status(self) -> str:
        """Current work_status."""
        return AVAILABLE_STATE[int(self.data["work_status"])]

    @property
    def mode(self) -> str:
        """Current mode."""
        return AVAILABLE_MODE[int(self.data["mode"])]

    @property
    def keeping_time(self) -> int:
        """Keeping last time in seconds."""
        return self.data["last_time"]
    
    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["voice"] == 0
    
    @property
    def keeping_temp(self) -> float:
        """Keeping last temperature."""
        return self.data["last_temp"]

    @property
    def temperature(self) -> float:
        """Current temperature."""
        return self.data["curr_tempe"]
    
    @property
    def cook_time(self) -> int:
        """How long the device has been active in seconds."""
        return self.data["cook_time"]

    @property
    def left_time(self) -> int:
        """Remaining cooking time in seconds."""
        return self.data["left_time"]

    @property
    def heat_power(self) -> int:
        return self.data["heat_power"]

    @property
    def warm_time(self) -> int:
        return self.data["warm_time"]

    @property
    def cook_status(self) -> int:
        return self.data["cook_status"]
    
    @property
    def cooked_time(self) -> int:
        return self.data["cooked_time"]

    @property
    def stand_top_num(self) -> int:
        return self.data["stand_top_num"]

    @property
    def mode_sort(self) -> str:
        return self.data["mode_sort"]

    @property
    def warm_data(self) -> str:
        return self.data["warm_data"]

    @property
    def work_temps(self) -> str:
        return self.data["work_temps"]

    def __repr__(self) -> str:
        s = (
            "<Health_PotStatus work_status=%s, "
            "mode=%s, "
            "temperature=%s, "
            "buzzer=%s>"
            % (
                self.work_status,
                self.mode,
                self.temperature,
                self.buzzer
            )
        )
        return s


class Health_Pot(Device):
    """Main class representing the Xiaomi Mijia Multifunctional."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_HEALTH_POT_1,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in SUPPORTED_MODELS.keys():
            self.model = model
        else:
            self.model = MODEL_HEALTH_POT_1

    @command(
        default_output=format_output(
            "",
            "Work status: {result.work_status}\n"
            "Temperature: {result.temperature} °C\n"
            "Mode: {result.mode}\n"
            "Buzzer: {result.buzzer}\n",
        )
    )
    def status(self) -> Health_PotStatus:
        """Retrieve properties."""
        properties = SUPPORTED_MODELS[self.model]["available_properties"]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props_per_request = 15

        # The MODEL_HEALTH_POT_1 is limited to a single property per request
        if self.model == MODEL_HEALTH_POT_1:
            _props_per_request = 1

        values = self.get_properties(properties, max_properties=_props_per_request)

        return Health_PotStatus(dict(zip(properties, values)))

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if buzzer:
            return self.send("set_voice", [0])
        else:
            return self.send("set_voice", [1])
