from typing import List, Optional

class Payload:
    def __init__(self, payload):
        self._payload = payload
        

class AccelerometerPayload(Payload):
    init: Optional[bool]
    range: Optional[float]
    x: Optional[float]
    y: Optional[float]
    z: Optional[float]


class AddressableLEDPayload(Payload):
    init: Optional[bool]


class AnalogInputPayload(Payload):
    init: Optional[bool]
    volatge: Optional[float]


class AnalogOutputPayload(Payload):
    init: Optional[bool]


class DigitalIOPayload(Payload):
    init: Optional[bool]
    duty_cycle: Optional[float]
    dio_pin: Optional[int]


class DutyCycleOutPayload(Payload):
    init: Optional[bool]
    duty_cycle: Optional[float]
    dio_pin: Optional[int]


class DriverStationPayload(Payload):
    new_data: Optional[bool]
    enabled: Optional[bool]
    autonomous: Optional[bool]
    test: Optional[bool]
    estop: Optional[bool]
    fms: Optional[bool]
    ds: Optional[bool]
    station: Optional[int]
    match_time: Optional[float]
    game_data: Optional[str]


class DutyCycleInputPayload(Payload):
    init: Optional[bool]
    connected: Optional[bool]
    position: Optional[float]


class EncoderPayload(Payload):
    init: Optional[bool]
    channel_a: Optional[int]
    channel_b: Optional[int]
    samples_to_avg: Optional[int]
    count: Optional[int]
    period: Optional[float]


class GyroPayload(Payload):
    init: Optional[bool]
    range: Optional[float]
    connected: Optional[bool]
    angle_x: Optional[float]
    angle_y: Optional[float]
    angle_z: Optional[float]
    rate_x: Optional[float]
    rate_y: Optional[float]
    rate_z: Optional[float]


class JoystickPayload(Payload):
    axes: Optional[List[float]]
    povs: Optional[List[int]]
    buttons: Optional[List[bool]]
    rumble_left: Optional[float]
    rumble_right: Optional[float]


class PCMPayload(Payload):
    pass


class PWMPayload(Payload):
    init: Optional[bool]
    speed: Optional[float]
    position: Optional[float]


class RelayPayload(Payload):
    init_fwd: Optional[bool]
    init_rev: Optional[bool]
    fwd: Optional[bool]
    rev: Optional[bool]


class SolenoidPayload(Payload):
    init = Optional[bool]
    output = Optional[bool]


class SimDevicePayload(Payload):
    pass


class RoboRIOPayload(Payload):
    pass
