# Xiaomi Mijia Multifunctional MJYSH01YM

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Donate](https://img.shields.io/badge/donate-Yandex-red.svg)](https://yoomoney.ru/to/410017564864143)

This is a custom component for home assistant to integrate the Xiaomi Mijia Multifunctional MJYSH01YM.

![Xiaomi Mijia Multifunctional MJYSH01YM](https://github.com/Sergey-SRG/Xiaomi-Mijia-Multifunctional-MJYSH01YM/blob/master/MJYSH01YM.jpg)

Please follow the instructions on [Retrieving the Access Token](https://home-assistant.io/components/xiaomi/#retrieving-the-access-token) to get the API token to use in the configuration.yaml file.

Credits: Thanks to [Rytilahti](https://github.com/rytilahti/python-miio) for all the work.

## Features

### viomi.health_pot.v1
![Interface](https://github.com/Sergey-SRG/Xiaomi-Mijia-Multifunctional-MJYSH01YM/blob/master/interface.jpg)
* Attributes
  - run_status
  - mode
  - last_time
  - last_temp
  - curr_tempe
  - heat_power
  - warm_time
  - cook_time
  - left_time"
  - cook_status
  - cooked_time
  - voice
  - stand_top_num
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
  name: Чайник
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
| `entity_id`               |      no  | Only act on a specific Kettle.                  |
| `voice`                   |       no | Specify the buzzer status (on/off).       |

#### Service `health_pot.set_work`

Set the working status of the device and his work mode.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      no  | Only act on a specific Kettle.     |
| `status`                  | no       | (1:Reservation 2:Cooking 3:Paused 4:Keeping 5:Stop)   |
| `id`                      | no       | Mode id, can have 24 modes .1-8 (custom) and 11-26 (inline) |
| `keep_temp`               | yes      | Keep temperature, 1-99   |
| `keep_time`               | yes      | Keep time, hours (1-12)|
| `timestamp`               | yes      | Timestamp of the reservation|

#### Service `health_pot.delete_modes`

Remove a custom mode.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      no  | Only act on a specific Kettle.     |
| `modes`                   | no       | Mode id, 1-8 (custom).    |

#### Service `health_pot.set_mode_sort`

Set mode sorting.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      no | Only act on a specific Kettle.     |
| `sort`                    | no      | Mode ID sort, 1-8 (custom). (11-12-13-23-15-16-17-18-20-26-21-14-19-25-24-22-1-2)   |

#### Service `health_pot.set_mode`

Configure custom mode properties. Firepower and duration can be specified.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      no  | Only act on a specific Kettle.     |
| `status`                  | no       | (1:Reservation 2:Cooking 3:Paused 4:Keeping 5:Stop)   |
| `id`                      | no       | Mode id, can have 24 modes .1-8 (custom) and 11-26 (inline) |
| `heat`                    | no       | Heat power, 1-99   |
| `time`                    | no       | Duration, minutes (1-240)|
