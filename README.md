# Xiaomi Mijia Multifunctional MJYSH01YM

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

This is a custom component for home assistant to integrate the Xiaomi Mijia Multifunctional MJYSH01YM.

![hacs_badge](https://imgservice1.suning.cn/uimg1/b2c/image/bL2eQvGQdSklY8VgCr4qTg.jpg_400w_400h_4e)

Please follow the instructions on [Retrieving the Access Token](https://home-assistant.io/components/xiaomi/#retrieving-the-access-token) to get the API token to use in the configuration.yaml file.

Credits: Thanks to [Rytilahti](https://github.com/rytilahti/python-miio) for all the work.

## Features

### viomi.health_pot.v1

* Sensors
  - run_status (16:No kettle placed  32:Drycooking protection 48:Both)
  - work_status (1:Reservation 2:Cooking 3:Paused 4:Keeping 5:Stop)
  - work_status_cn 
  - warm_data
  - last_time
  - last_temp
  - curr_tempe
  - mode (Mode ID)
  - mode_en (Mode Name for English)
  - mode_cn (中文模式名称)
  - heat_power
  - warm_time
  - cook_time
  - left_time
  - cook_status
  - cooked_time
  - voice
  - stand_top_num
  - mode_sort
* Chart
  - TODO: Temperature History (Like the temperature chart of the weather forecast)
* Services
  - set_voice
  - set_work
  - delete_modes
  - set_mode_sort
  - set_mode

## Setup

```yaml
# configuration.yaml

health_pot: 
  host: 192.168.1.13
  token: a9bd32552dc9bd4e156954c20ddbcb38
  name: 养生壶
  model: viomi.health_pot.v1
  scan_interval: 10
```

Configuration variables:
- **host** (*Required*): The IP of your cooker.
- **token** (*Required*): The API token of your cooker.
- **name** (*Optional*): The name of your cooker.
- **model** (*Optional*): Currently only support viomi.health_pot.v1
- **scan_interval** (*Optional*): Data update interval

## Platform services

#### Service `health_pot.set_voice`

Set whether the buzzer is enabled.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific Kettle.                  |
| `voice`                 |       no | Specify the buzzer status (on/off).       |

#### Service `health_pot.set_work`

Set the working status of the device and his work mode.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific Kettle.     |
| `status`                  | yes      | (1:Reservation 2:Cooking 3:Paused 4:Keeping 5:Stop)   |
| `id`                      | yes      | Mode id, can have 24 modes .1-8 (custom) and 11-26 (inline) |
| `keep_temp`               | yes      | Keep temperature, 1-99   |
| `keep_time`               | yes      | Keep time, hours (1-12)|
| `timestamp`               | yes      | Timestamp of the reservation|

#### Service `health_pot.delete_modes`

Remove a custom mode.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific Kettle.     |
| `modes`                   | yes      | Mode id, 1-8 (custom).    |

#### Service `health_pot.set_mode_sort`

Set mode sorting.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific Kettle.     |
| `sort`                    | yes      | Mode ID sort, 1-8 (custom). (11-12-13-23-15-16-17-18-20-26-21-14-19-25-24-22-1-2)   |

#### Service `health_pot.set_mode`

Configure custom mode properties. Firepower and duration can be specified.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific Kettle.     |
| `status`                  | yes      | (1:Reservation 2:Cooking 3:Paused 4:Keeping 5:Stop)   |
| `id`                      | yes      | Mode id, can have 24 modes .1-8 (custom) and 11-26 (inline) |
| `heat`                    | yes      | Heat power, 1-99   |
| `time`                    | yes      | Duration, minutes (1-240)|
