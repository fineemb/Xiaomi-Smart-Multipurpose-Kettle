from collections import defaultdict
import asyncio
from datetime import timedelta
from functools import partial
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import discovery
from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
    CONF_TOKEN,
    CONF_SCAN_INTERVAL,
    ATTR_ENTITY_ID,
)
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.event import track_time_interval
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.util.dt import utcnow
from miio import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Mi Smart Multipurpose Kettle"
DOMAIN = "health_pot"
DATA_KEY = "health_pot_data"


SERVICE_SET_VOICE = "set_voice"
SERVICE_SET_WORK = "set_work"
SERVICE_DELETE_MODES = "delete_modes"
SERVICE_SET_MODE_SORT = "set_mode_sort"
SERVICE_SET_MODE = "set_mode"

AVAILABLE_STATE = {
    0 : "stopped",
    1 : "reservation",
    2 : "cooking",
    3 : "paused",
    4 : "keeping",
    5 : "stop"
}

AVAILABLE_RUN_STATUS = {
    0  : "On base",
    16 : "No kettle placed",
    32 : "Drycooking protection",
    48 : "Both"
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

ATTR_MODEID = "id"
ATTR_MODETEMP = "temp"
ATTR_MODETIME = "time"
ATTR_DELMODES = "modes"
ATTR_VOICE = "voice"
ATTR_MODE_SORT = "sort"
ATTR_WORK_STATUS = "status"
ATTR_WORK_MODEID = "id"
ATTR_WORK_KTEMP = "keep_temp"
ATTR_WORK_KTIME = "keep_time"
ATTR_WORK_TS = "timestamp"

SCAN_INTERVAL = timedelta(seconds=30)

CONF_MODEL = "model"

MODEL_NORMAL1 = "viomi.health_pot.v1"

SUPPORTED_MODELS = [
    MODEL_NORMAL1
]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Optional(CONF_MODEL): vol.In(SUPPORTED_MODELS),
                vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_SCHEMA_SET_MODE = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_id,
    vol.Required(ATTR_MODEID): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
    vol.Required(ATTR_MODETEMP): vol.All(vol.Coerce(int), vol.Range(min=1, max=99)),
    vol.Required(ATTR_MODETIME): vol.All(vol.Coerce(int), vol.Range(min=1, max=240))
})
SERVICE_SCHEMA_SET_WORK = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_id,
    vol.Required(ATTR_WORK_STATUS): vol.All(vol.Coerce(int), vol.Range(min=1, max=5)),
    vol.Required(ATTR_WORK_MODEID): vol.All(vol.Coerce(int), vol.Range(min=1, max=26)),
    vol.Optional(ATTR_WORK_KTEMP, default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=95)),
    vol.Optional(ATTR_WORK_KTIME, default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=12)),
    vol.Optional(ATTR_WORK_TS, default=0): vol.All(vol.Coerce(int))
})

SERVICE_SCHEMA_DEL_MODES = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_id,
    vol.Required(ATTR_DELMODES): vol.All(vol.Coerce(int), vol.Range(min=1, max=8))
})
SERVICE_SCHEMA_SET_VOICE = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_id,
    vol.Required(ATTR_VOICE): vol.All(vol.Coerce(str), vol.Clamp('off', 'on'))
})
SERVICE_SCHEMA_SET_MODE_SORT = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_id,
    vol.Required(ATTR_MODE_SORT): vol.All(vol.Coerce(str))
})


ATTR_MODEL = "model"
ATTR_PROFILE = "profile"
SUCCESS = ["ok"]

SERVICE_SCHEMA = vol.Schema(
    {
        #    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
    }
)
SERVICE_SCHEMA_START = SERVICE_SCHEMA.extend({vol.Required(ATTR_PROFILE): cv.string})

SERVICE_START = "start"
SERVICE_STOP = "stop"

def setup(hass, config):
#    from miio import Device, DeviceException
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    host = config[DOMAIN][CONF_HOST]
    token = config[DOMAIN][CONF_TOKEN]
    name = config[DOMAIN][CONF_NAME]
    model = config[DOMAIN].get(CONF_MODEL)
    scan_interval = config[DOMAIN][CONF_SCAN_INTERVAL]

    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}
        hass.data[DATA_KEY][host] = {}
    
    _LOGGER.info("Initializing with host %s (token %s...)", host, token[:5])
    
    devices = []
    if model is None:
        try:
            miio_device = Device(host, token)
            device_info = miio_device.info()
            model = device_info.model
            _LOGGER.info(
                "%s %s %s detected",
                model,
                device_info.firmware_version,
                device_info.hardware_version,
            )
        except DeviceException:
            raise PlatformNotReady
        
    if model not in SUPPORTED_MODELS:

        _LOGGER.error(
            "Unsupported device found! Please create an issue at "
            "https://github.com/fineemb/Xiaomi-Smart-Multipurpose-Kettle/issues "
            "and provide the following data: %s",
            model,
        )
        return False

    def update(event_time):
        """Get the latest data and updates the states."""
        try:
            miio_device = Device(host, token)

            run_status    =  miio_device.send('get_prop', ["run_status"])[0]
            work_status   =  miio_device.send('get_prop', ["work_status"])[0]
            #warm_data     =  miio_device.send('get_prop', ["warm_data"])[0]
            last_time     =  miio_device.send('get_prop', ["last_time"])[0]
            last_temp     =  miio_device.send('get_prop', ["last_temp"])[0]
            curr_tempe    =  miio_device.send('get_prop', ["curr_tempe"])[0]
            # work_temps    =  miio_device.send('get_prop', ["work_temps"])[0]
            mode          =  miio_device.send('get_prop', ["mode"])[0] #模式
            heat_power    =  miio_device.send('get_prop', ["heat_power"])[0] #功率
            warm_time     =  miio_device.send('get_prop', ["warm_time"])[0] #保温时间
            cook_time     =  miio_device.send('get_prop', ["cook_time"])[0] #蒸煮时间
            left_time     =  miio_device.send('get_prop', ["left_time"])[0] #剩余时间
            cook_status   =  miio_device.send('get_prop', ["cook_status"])[0] #蒸煮状态
            cooked_time   =  miio_device.send('get_prop', ["cooked_time"])[0]
            voice         =  miio_device.send('get_prop', ["voice"])[0]
            stand_top_num =  miio_device.send('get_prop', ["stand_top_num"])[0]
            #mode_sort     =  miio_device.send('get_prop', ["mode_sort"])[0]

            __state_attrs = {
                "run_status":AVAILABLE_RUN_STATUS[int(run_status)],
                "mode":AVAILABLE_MODE[int(mode)],
                "last_time":last_time,
                "last_temp":last_temp,
                "curr_tempe":curr_tempe,
                # "work_temps":work_temps,
                "heat_power":heat_power,
                "warm_time":warm_time,
                "cook_time":cook_time,
                "left_time":left_time,
                "cook_status":cook_status,
                "cooked_time":cooked_time,
                "voice":voice,
                "stand_top_num":stand_top_num,
                #"mode_sort":mode_sort,
                #"warm_data":warm_data,
                "friendly_name":name
            }

            unique_id = "{}_{}".format("xiaomi", miio_device.info().mac_address.replace(':', ''))
            entityid = "{}.{}".format(DOMAIN,unique_id)
            hass.states.set(entityid, AVAILABLE_STATE[int(work_status)], __state_attrs)

        except DeviceException:
            _LOGGER.exception('Fail to get_prop from XiaomiHealthPot')
            raise PlatformNotReady

    track_time_interval(hass, update, scan_interval)

    def set_voice(voice: str):
        try:
            miio_device = Device(host, token)
            if voice == 'on':
                miio_device.send('set_voice', [0])
            elif voice == 'off':
                miio_device.send('set_voice', [1])
        except DeviceException:
            raise PlatformNotReady
        
    def set_work(**kwargs):
        """Set work."""
        try:
            miio_device = Device(host, token)
            miio_device.send('set_work', [kwargs["status"],kwargs["id"],kwargs["keep_temp"],kwargs["keep_time"],kwargs["timestamp"]])
        except DeviceException:
            raise PlatformNotReady

    def delete_modes(**kwargs):
        """Delete work.删除自定义模式"""
        try:
            miio_device = Device(host, token)
            miio_device.send('delete_modes', [kwargs["modes"]])
        except DeviceException:
            raise PlatformNotReady
    
    def set_mode_sort(**kwargs):
        """Set mode sort.设置模式排序"""
        try:
            miio_device = Device(host, token)
            miio_device.send('set_mode_sort', [kwargs["sort"]])
        except DeviceException:
            raise PlatformNotReady
    
    def set_mode(**kwargs):
        """Set mode.设置自定义模式"""
        try:
            miio_device = Device(host, token)
            miio_device.send('set_mode', [kwargs["id"],kwargs["heat"],kwargs["time"]])
        except DeviceException:
            raise PlatformNotReady

    def service_handle(service):
        params = {key: value for key, value in service.data.items()}

        if service.service == SERVICE_SET_VOICE:
            set_voice(**params)

        if service.service == SERVICE_SET_WORK:
            set_work(**params)

        if service.service == SERVICE_DELETE_MODES:
            delete_modes(**params)

        if service.service == SERVICE_SET_MODE_SORT:
            set_mode_sort(**params)

        if service.service == SERVICE_SET_MODE:
            set_mode(**params)

    hass.services.register(DOMAIN, SERVICE_SET_VOICE, service_handle, schema=SERVICE_SCHEMA_SET_VOICE)
    hass.services.register(DOMAIN, SERVICE_SET_WORK, service_handle, schema=SERVICE_SCHEMA_SET_WORK)
    hass.services.register(DOMAIN, SERVICE_DELETE_MODES, service_handle, schema=SERVICE_SCHEMA_DEL_MODES)
    hass.services.register(DOMAIN, SERVICE_SET_MODE_SORT, service_handle, schema=SERVICE_SCHEMA_SET_MODE_SORT)
    hass.services.register(DOMAIN, SERVICE_SET_MODE, service_handle, schema=SERVICE_SCHEMA_SET_MODE)
    
    return True